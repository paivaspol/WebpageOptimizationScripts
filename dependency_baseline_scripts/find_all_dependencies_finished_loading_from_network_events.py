from argparse import ArgumentParser 

import common_module
import os
import simplejson as json
import numpy

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = common_module.get_pages(args.page_list)

    failed_pages = []
    for page in pages:

        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            failed_pages.append(page)
            continue
        dependencies = common_module.get_dependencies(dependency_filename)
        dependency_finish_download_time = get_dependency_finish_download_time(page, \
                                                                              network_filename, \
                                                                              dependencies)
        if len(dependency_finish_download_time) > 0:
            if not args.use_median_finish_time:
                print '{0} {1}'.format(page, max(dependency_finish_download_time.values()))
            else:
                print '{0} {1}'.format(page, numpy.median(dependency_finish_download_time.values()))
        else:
            failed_pages.append(page)
    print 'Failed Pages: ' + str(failed_pages)

def get_dependency_finish_download_time(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        times_from_first_request = dict()
        found_first_request = False
        first_request_timestamp = -1
        request_id_to_url_map = dict()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = network_event[PARAMS][TIMESTAMP]
                    else:
                        continue
                
                request_id_to_url_map[request_id] = url

            elif network_event[METHOD] == 'Network.loadingFinished':
                request_id = network_event[PARAMS][REQUEST_ID]
                if request_id in request_id_to_url_map:
                    url = request_id_to_url_map[request_id]

                    if url in dependencies and url not in times_from_first_request:
                        # We have already discovered all the dependencies.
                        # Get the current timestamp and find the time difference.
                        finish_timestamp = network_event[PARAMS][TIMESTAMP]
                        time_from_first_request = finish_timestamp - first_request_timestamp
                        if args.print_ms:
                            time_from_first_request = time_from_first_request * 1000.0
                        times_from_first_request[url] = time_from_first_request

                        dependencies.remove(url)
                        
                        if len(dependencies) == 0:
                            break

        return times_from_first_request

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--use-median-finish-time', default=False, action='store_true')
    parser.add_argument('--print-ms', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
