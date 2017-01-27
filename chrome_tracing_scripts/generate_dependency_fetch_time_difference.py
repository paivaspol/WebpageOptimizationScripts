from argparse import ArgumentParser
from collections import defaultdict

import constants
import common_module
import os
import simplejson as json

def main(root_dirs, page_list, dependency_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = common_module.get_pages_with_redirection(page_list)
    for page_tuple in pages:
        page, page_r = page_tuple
        print page
        url_fetch_times = defaultdict(list)
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(dependency_filename)):
            continue
        dependencies = get_dependencies(dependency_filename)
        for root_dir in root_dirs:
            network_filename = os.path.join(root_dir, page_r, 'network_' + page_r)
            if not os.path.exists(network_filename):
                continue
            page_url_fetch_times = get_url_fetch_times(network_filename, page_r, dependencies)
            for url in page_url_fetch_times:
                url_fetch_times[url].append(page_url_fetch_times[url])
        output_to_file(output_dir, page_r, url_fetch_times)

def output_to_file(output_dir, page, data):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        sorted_data = sorted(data.iteritems(), key=lambda x: x[1][0])
        for url, times in sorted_data:
            output_line = url
            for t in times:
                output_line += ' ' + str(t)
            try:
                output_line += ' ' + str((times[1] - times[0]))
                output_file.write(output_line + '\n')
            except:
                pass

def get_url_fetch_times(network_filename, page, dependencies):
    url_fetch_times = dict()
    request_id_to_url = dict()
    seen_urls = set()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        first_request_timestamp = -1
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == constants.NET_REQUEST_WILL_BE_SENT:
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if not found_first_request:
                    if common_module.escape_page(url) == page.strip():
                        found_first_request = True
                        first_request_timestamp = float(network_event[constants.PARAMS][constants.TIMESTAMP])
                    else:
                        continue
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if url in dependencies and url not in seen_urls:
                    timestamp = network_event[constants.PARAMS][constants.TIMESTAMP]
                    request_id_to_url[request_id] = url
                    seen_urls.add(url)

            elif network_event[constants.METHOD] == constants.NET_LOADING_FINISHED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in request_id_to_url:
                    url = request_id_to_url[request_id]
                    timestamp = float(network_event[constants.PARAMS][constants.TIMESTAMP])
                    url_fetch_time = timestamp - first_request_timestamp
                    url_fetch_times[url] = url_fetch_time
    return url_fetch_times

def get_dependencies(dependency_filename):
    dependencies = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            splitted_line = raw_line.strip().split()
            url = splitted_line[2]
            priority = splitted_line[6]
            # if priority == 'Important' or priority == 'Semi-important':
            # if priority == 'Important':
            dependencies.add(url)
    return dependencies

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir', nargs='+')
    parser.add_argument('page_list')
    parser.add_argument('dependency_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.page_list, args.dependency_dir, args.output_dir)
