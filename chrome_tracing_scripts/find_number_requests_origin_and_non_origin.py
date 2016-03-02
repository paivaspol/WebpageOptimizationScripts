from argparse import ArgumentParser

import common_module
import simplejson as json
import re
import os

def find_number_of_requests(root_dir):
    result = dict()
    plt_dict = dict()
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        network_filename = os.path.join(path, 'network_' + url)
        page_start_end_time_filename = os.path.join(path, 'start_end_time_' + url)
        start_time, end_time = common_module.parse_page_start_end_time(page_start_end_time_filename)[2]
        unique_requests = set()
        non_origin_requests = set()
        with open(network_filename, 'rb') as input_file:
            for raw_line in input_file:
                network_event = json.loads(json.loads(raw_line.strip()))
                if network_event['method'] == 'Network.requestWillBeSent':
                    event_ts = network_event['params']['timestamp'] * 1000.0
                    if start_time <= event_ts <= end_time:
                        request_id = network_event['params']['requestId']
                        unique_requests.add(request_id)
                        document_url = network_event['params']['documentURL']
                        if url not in network_event['params']['request']['url']:
                            # This is requested from the origin HTML
                            # Find out whether the requested resource is also within 
                            # the same origin or not.
                            non_origin_requests.add(request_id)

        result[url] = (len(unique_requests), len(non_origin_requests))
        plt_dict[url] = end_time - start_time
    

    sorted_plt = sorted(plt_dict.items(), key=lambda x: x[1])
    for plt_obj in sorted_plt:
        print '{0} {1} {2} {3}'.format(plt_obj[0], plt_obj[1], result[plt_obj[0]][0], result[plt_obj[0]][1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    find_number_of_requests(args.root_dir)

