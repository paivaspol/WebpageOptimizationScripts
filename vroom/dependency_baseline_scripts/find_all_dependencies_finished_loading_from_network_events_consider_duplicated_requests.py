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

        dependencies = common_module.get_dependencies(dependency_filename, args.only_important_resources)
        # dependencies = common_module.get_dependencies_without_other_iframes(dependency_filename, \
        #                                                                 args.only_important_resources, \
        #                                                                 page)
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
        
        # Output the dependencies to the output directory if possible.
        if args.output_finish_times:
            if not os.path.exists(args.output_finish_times):
                os.mkdir(args.output_finish_times)
            output_to_file(args.output_finish_times, page, dependency_finish_download_time)
    if args.print_failed_pages:
        print 'Failed Pages: ' + str(failed_pages)

def output_to_file(output_dir, filename, dependency_finish_load_times):
    output_filename = os.path.join(output_dir, filename)
    with open(output_filename, 'wb') as output_file:
        for url, dependency_finish_load_time in dependency_finish_load_times.iteritems():
            output_file.write('{0} {1}\n'.format(url, dependency_finish_load_time))

def get_dependency_finish_download_time(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        times_from_first_request = dict()
        found_first_request = False
        first_request_timestamp = -1
        request_id_to_url_map = dict()
        served_from_cache = set()
        seen_url = set()
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except Exception:
                network_event = json.loads(raw_line.strip())
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                url = network_event[PARAMS][REQUEST][URL]

                # if 'redirectResponse' in network_event[PARAMS]:
                #     url = network_event[PARAMS]['redirectResponse']['url']

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = network_event[PARAMS][TIMESTAMP]
                    else:
                        continue
                
                if not url.startswith('data:') and url != 'about:blank':
                    request_id_to_url_map[request_id] = url

            elif found_first_request and network_event['method'] == 'Network.requestServedFromCache':
                request_id = network_event['params']['requestId']
                if request_id in request_id_to_url_map:
                    served_from_cache.add(request_id)
                
            elif found_first_request and network_event['method'] == 'Network.responseReceived':
                request_id = network_event['params']['requestId']
                if request_id in request_id_to_url_map:
                    if network_event['params']['response']['fromDiskCache']:
                        served_from_cache.add(request_id)

            elif found_first_request and (network_event[METHOD] == 'Network.loadingFinished' or \
                    network_event[METHOD] == 'Network.loadingFailed'):
                request_id = network_event[PARAMS][REQUEST_ID]
                if request_id in request_id_to_url_map:
                    url = request_id_to_url_map[request_id]
                    # We have already discovered all the dependencies.
                    # Get the current timestamp and find the time difference.
                    finish_timestamp = network_event[PARAMS][TIMESTAMP]
                    time_from_first_request = finish_timestamp - first_request_timestamp
                    if args.print_ms:
                        time_from_first_request = time_from_first_request * 1000.0
                    times_from_first_request[url] = time_from_first_request

        return times_from_first_request

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--use-median-finish-time', default=False, action='store_true')
    parser.add_argument('--print-ms', default=False, action='store_true')
    parser.add_argument('--output-finish-times', default=None)
    parser.add_argument('--only-important-resources', default=False, action='store_true')
    parser.add_argument('--print-failed-pages', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
