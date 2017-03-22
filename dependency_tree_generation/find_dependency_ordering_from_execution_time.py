from argparse import ArgumentParser
from urlparse import urlparse
from collections import defaultdict

import common_module
import os

THRESHOLD = 0.4

def main(root_dir, dependency_dir, page_list, iterations, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for base_page, page in page_list:
        # print 'processing: ' + page
        orderings = []
        escaped_page = common_module.escape_url(page)
        escaped_base_page = common_module.escape_url(base_page)
        dependency_filename = os.path.join(dependency_dir, escaped_base_page, 'dependency_tree.txt')
        if not os.path.exists(dependency_filename):
            dependency_filename = os.path.join(dependency_dir, escaped_page, 'dependency_tree.txt')

        if not os.path.exists(dependency_filename):
            print 'Missing dependency tree file: ' + page + ' escaped_page: ' + escaped_base_page
            continue
        dependencies = get_dependencies(dependency_filename)
        devtools_request_intersections = find_devtools_request_intersection(root_dir, iterations, escaped_page)

        start_iteration = 0
        if args.skip_first_load:
            start_iteration = 1
        for i in range(start_iteration, iterations):
            processing_time_filename = os.path.join(root_dir, 'extended_waterfall_' + str(i), 
                                                    escaped_page, 'processing_time.txt')
            if not os.path.exists(processing_time_filename):
                continue
            iter_ordering = parse_processing_time_file(processing_time_filename, escaped_page)
            orderings.append(iter_ordering)
        print orderings
        if len(orderings) > 0:
            # check_domain_orderings('s.yimg.com', orderings)
            # output_orderings(orderings)
            order_index = check_orderings(orderings)
            if order_index < 0:
                order_index = 0
            output_orderings_to_file(root_dir, orderings, dependencies, output_dir, escaped_page, order_index, devtools_request_intersections, escaped_base_page)
        else:
            print 'No orderings'

def find_devtools_request_intersection(root_dir, iterations, page):
    result = set()
    first_iteration = True
    start_iteration = 0
    if args.skip_first_load:
        start_iteration = 1
    for i in range(start_iteration, iterations):
        request_filename = os.path.join(root_dir, 'extended_waterfall_' + str(i),
                                        page, 'ResourceSendRequest.txt')
        if not os.path.exists(request_filename):
            continue

        with open(request_filename, 'rb') as input_file:
            cur_iteration = set()
            for line in input_file:
                cur_iteration.add(line.strip().split()[0])
            if first_iteration:
                result |= cur_iteration
                first_iteration = False
            else:
                result &= cur_iteration
    return result

def get_urls_from_extended_waterfall_file(filename):
    urls = set()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            urls.add(line[0])
    return urls

def get_dependencies(dependency_filename):
    result = dict()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[2]
            result[url] = line
    return result

def output_orderings_to_file(root_dir, orderings, dependencies, output_dir, page, order_index, devtools_request_intersection, escaped_base_page):
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))
    output_filename = os.path.join(output_dir, escaped_base_page, 'dependency_tree.txt')
    if not os.path.exists(os.path.join(output_dir, escaped_base_page)):
        os.mkdir(os.path.join(output_dir, escaped_base_page))
    file_index = order_index
    if args.skip_first_load:
        file_index = order_index + 1
    plt_filename = os.path.join(root_dir, str(file_index), page, 'start_end_time_' + page)
    request_filename = os.path.join(root_dir, 'extended_waterfall_' + str(file_index),
                                    page, 'ResourceSendRequest.txt')
    fetch_filename = os.path.join(root_dir, 'extended_waterfall_' + str(file_index),
                                    page, 'ResourceFinish.txt')
    plt = get_plt(plt_filename)
    fetch_times = get_fetch_times(request_filename, fetch_filename)
    with open(output_filename, 'wb') as output_file:
        print 'Writing to ' + output_filename
        for obj in orderings[order_index]:
            print obj
            if obj in dependencies and obj in devtools_request_intersection:
                line = dependencies[obj]
                vroom_priority = infer_vroom_priority(plt, fetch_times[obj], line[4], line[5])
                output_line = line[0] + ' ' + line[1] + ' ' + obj + ' ' + line[3] + ' ' + line[4] + ' ' + line[5] + ' ' + vroom_priority
                output_file.write(output_line + '\n')
                del dependencies[obj]
        sorted_dependencies = sorted(dependencies.iteritems(), key=lambda x: x[1][3])
        for obj, line in sorted_dependencies:
            if obj in devtools_request_intersection:
                output_line = ''
                for token in line:
                    output_line += token + ' '
                if obj in fetch_times:
                    vroom_priority = infer_vroom_priority(plt, fetch_times[obj], line[4], line[5])
                    output_line += vroom_priority
                    output_file.write(output_line.strip() + '\n')

def get_fetch_times(send_request_filename, finish_filename):
    request_times = dict()
    finish_times = dict()
    with open(send_request_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            request_times[line[0]] = int(line[2])
    with open(finish_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            finish_times[line[0]] = int(line[2])

    fetch_times = dict()
    for url in finish_times:
        fetch_times[url] = (finish_times[url] - request_times[url]) / 1000.0
    return fetch_times

def get_plt(plt_filename):
    with open(plt_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return float(line[2]) - float(line[1])

def infer_vroom_priority(plt, obj_fetch_time, resource_type, request_priority):
    fraction_of_plt = 1.0 * obj_fetch_time / plt
    if ((resource_type == 'Stylesheet' or resource_type == 'Script') and \
        (request_priority == 'VeryHigh' or request_priority == 'High' or request_priority == 'Medium')) or \
        (resource_type == 'Document' or resource_type == 'XHR'):
        return 'Important'
    # elif (resource_type == 'Document' or resource_type == 'Stylesheet' or resource_type == 'Script') or \
    #     fraction_of_plt > THRESHOLD:
    elif (resource_type == 'Document' or resource_type == 'Stylesheet' or resource_type == 'Script'):
        return 'Semi-important'
    else:
        return 'Unimportant'

def output_orderings(orderings):
    first_round = orderings[0]
    for url in first_round:
        print url

def check_domain_orderings(domain, orderings):
    domain_orderings = []
    for ordering in orderings:
        domain_ordering = []
        for url in ordering:
            parsed_url = urlparse(url)
            if parsed_url.netloc == domain:
                domain_ordering.append(url)
        domain_orderings.append(domain_ordering)
    check_ordering_lists(domain_orderings)

def check_orderings(orderings):
    # First check if the lengths are different
    length_histogram = defaultdict(list)
    max_length = -1
    for i, ordering in enumerate(orderings):
        length_histogram[len(ordering)].append(i)
        max_length = max(max_length, len(ordering))

    length_different = len(length_histogram) != 1

    if length_different:
        print '\t[WARNING] Length different: {0}'.format(length_histogram.keys())
        # for i, ordering in enumerate(orderings):
        #     print '\tordering {0}: '.format(i) + str(ordering)
        # return False

    # Check if we have a majority of lenghts from the orderings, if so, use that subset.
    if (1.0 * max_length / len(orderings)) <= 0.5:
        return -1

    new_orderings = [ orderings[i] for i in length_histogram[max_length] ]

    # Check the actual values
    return check_ordering_lists(new_orderings)

def check_ordering_lists(orderings):
    # Check for all pairs.
    for k in range(0, len(orderings)):
        first_round_length = len(orderings[k])
        found_mismatch = False
        mismatched_at = -1
        for j in range(k + 1, len(orderings)):
            for i in range(0, first_round_length):
                first_round_value = orderings[k][i]
                # print 'first round value: ' + first_round_value + ' other: ' + orderings[j][i]
                if first_round_value != orderings[j][i]:
                    print '\t[FAILED] Mismatch between rounds: {0} and {1}'.format(k, j)
                    print '\t[FAILED] Mismatch at round: {0} row: {1}'.format(j, i)
                    print '\t[FAILED] first round val: {0}, mismatched value: {1}'.format(first_round_value, orderings[j][i])
                    # print '\t[FAILED] orderings: {0}'.format(orderings)
                    found_mismatch = True
                    mismatched_at = j
                    break
            if found_mismatch:
                break
        if not found_mismatch:
            # We found an ordering.
            print '\t[SUCCESS] Match between rounds: {0} and {1}'.format(k, mismatched_at)
            return k
    # print '\t[PASSED]'
    return -1

def parse_processing_time_file(processing_time_filename, page):
    result = []
    url_found = set()
    with open(processing_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            start_processing_time = int(line[2])
            if common_module.escape_url(url) != page:
                if url not in url_found:
                    result.append( (url, start_processing_time) )
                    url_found.add(url)
    result.sort(key=lambda x: x[1])
    print result
    return [ x[0] for x in result ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_filename')
    parser.add_argument('dependency_dir')
    parser.add_argument('iterations', type=int)
    parser.add_argument('output_dir')
    parser.add_argument('--skip-first-load', default=False, action='store_true')
    args = parser.parse_args()
    page_list = common_module.get_pages_with_redirection(args.pages_filename)
    main(args.root_dir, args.dependency_dir, page_list, args.iterations, args.output_dir)
