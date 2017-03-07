from argparse import ArgumentParser

import common_module
import os
import subprocess

def main(root_dir, pages, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for page_tuple in pages:
        page, redirected_page = page_tuple
        # We need to get two files:
        #  - Dependency graph
        #  - Timings (have to aggregate across extended waterfall files.)
        page_extended_waterfall = os.path.join(root_dir, 'extended_waterfall', redirected_page)
        request_filename = os.path.join(page_extended_waterfall, 'ResourceSendRequest.txt')
        response_filename = os.path.join(page_extended_waterfall, 'ResourceReceiveResponse.txt')
        fetch_filename = os.path.join(page_extended_waterfall, 'ResourceFinish.txt')
        processing_times_filename = os.path.join(page_extended_waterfall, 'processing_time.txt')

        if not (os.path.exists(request_filename) and \
                os.path.exists(response_filename) and \
                os.path.exists(fetch_filename)):
            print '{0} missing extended waterfall files...'.format(page)
            continue

        dependency_filename = os.path.join(root_dir, 'dependencies', 'raw_dependency_tree', redirected_page + '.json')
        if not os.path.exists(dependency_filename):
            print '{0} missing dependency file...'.format(page)
            continue

        # Aggregate the timings
        timings = get_timings(request_filename, response_filename, fetch_filename)
        processing_times, start_processing_times = get_processing_times(processing_times_filename)

        # Create the output directory
        page_output_directory = os.path.join(output_dir, redirected_page)
        if not os.path.exists(page_output_directory):
            os.mkdir(page_output_directory)

        # Copy the dependency file to the output directory.
        cp_cmd = 'cp {0} {1}'.format(dependency_filename, \
                                     os.path.join(page_output_directory, 'dep_tree.json'))
        subprocess.call(cp_cmd.split())

        # Generate the timings file.
        output_filename = os.path.join(page_output_directory, \
                                      'timings.txt')
        with open(output_filename, 'wb') as output_file:
            for url, timing in timings.iteritems():
                if url in processing_times:
                    output_file.write('{0} {1} {2} {3} {4} {5}\n'.format(url, \
                                                               timing[0], \
                                                               timing[1], \
                                                               timing[2], \
                                                               start_processing_times[url], \
                                                               processing_times[url]))

def get_timings(request_filename, response_filename, fetch_filename):
    request_timings = populate_timings(request_filename)
    response_timings = populate_timings(response_filename)
    fetch_timings = populate_timings(fetch_filename)
    
    timings = dict()
    # Aggregate the timings
    for url in request_timings:
        if url in response_timings and url in fetch_timings:
            timing_tuple = ( request_timings[url], \
                             response_timings[url], \
                             fetch_timings[url] )
            timings[url] = timing_tuple
    return timings

def get_processing_times(filename):
    result = dict()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            start_processing_time = int(line[2])
            end_processing_time = int(line[3])
            if url not in result:
                result[url] = [ ]
            result[url].append(start_processing_time)
            result[url].append(end_processing_time)
    final_result = dict()
    start_processing_times = dict()
    for url in result:
        sorted_processing_time = sorted(result[url])
        final_result[url] = sorted_processing_time[-1] - sorted_processing_time[0]
        start_processing_times[url] = sorted_processing_time[0]
    return final_result, start_processing_times

def populate_timings(filename):
    result = dict()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            time = line[2]
            if url not in result:
                result[url] = time
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    pages = common_module.get_pages(args.pages_filename)
    main(args.root_dir, pages, args.output_dir)
