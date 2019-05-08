from argparse import ArgumentParser 

import common_module
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
TIMESTAMP = 'timestamp'
RESPONSE = 'response'
REQUEST = 'request'
REQUEST_ID = 'requestId'
STATUS = 'status'
URL = 'url'

def main(root_dir, page_list, dependency_dir):
    # pages = common_module.get_pages_with_redirection(page_list)
    failed_pages = []
    pages = common_module.get_pages_with_redirection(page_list)
    for page in pages:
        page_r = page[1]
        page = page[0]
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not os.path.exists(dependency_filename):
            dependency_filename = os.path.join(dependency_dir, page)
        # network_filename = os.path.join(root_dir, page_r, 'network_' + page)
        network_filename = os.path.join(root_dir, page_r, 'network_' + page_r)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            print 'Failed: ' + page
            failed_pages.append(page)
            continue
        dependencies = common_module.get_dependencies(dependency_filename, args.only_important_resources)
        dependency_finish_download_time = get_dependency_finish_download_time(page_r, \
                                                                              network_filename, \
                                                                              dependencies)
        if len(dependency_finish_download_time) > 0:
            print '{0} {1}'.format(page_r, max(dependency_finish_download_time.values()))
        else:
            failed_pages.append(page)

        # Output the dependencies to the output directory if possible.
        if args.output_discovery_times:
            if not os.path.exists(args.output_discovery_times):
                os.mkdir(args.output_discovery_times)
            output_to_file(args.output_discovery_times, page, dependency_finish_download_time)
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
        completed_urls = set()
        request_id_to_url = dict()
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except Exception:
                network_event = json.loads(raw_line.strip())
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                request_id = network_event[PARAMS][REQUEST_ID]
                url = network_event[PARAMS][REQUEST][URL]
                timestamp = network_event[PARAMS][TIMESTAMP]

                # Make sure to find the first request before parsing the file.
                if not found_first_request:
                    parsed_url = common_module.escape_page(url)
                    if parsed_url == page:
                        found_first_request = True
                        first_request_timestamp = timestamp
                    else:
                        continue

                if url in dependencies and url not in times_from_first_request:
                    # We have already discovered all the dependencies.
                    # Get the current timestamp and find the time difference.
                    time_since_first_request = timestamp - first_request_timestamp
                    times_from_first_request[url] = time_since_first_request
                    request_id_to_url[request_id] = url
                    dependencies.remove(url)
            elif found_first_request and (network_event[METHOD] == 'Network.loadingFinished' or \
                    network_event[METHOD] == 'Network.loadingFailed'):
                request_id = network_event[PARAMS][REQUEST_ID]
                if request_id in request_id_to_url:
                    url = request_id_to_url[request_id]
                    completed_urls.add(url)
        
        urls_to_remove = []
        for url in times_from_first_request:
            if url not in completed_urls:
                urls_to_remove.append(url)

        for url in urls_to_remove:
            del times_from_first_request[url]

        return times_from_first_request

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('dependency_dir')
    parser.add_argument('--only-important-resources', default=False, action='store_true')
    parser.add_argument('--print-failed-pages', default=False, action='store_true')
    parser.add_argument('--output-discovery-times', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.page_list, args.dependency_dir)
