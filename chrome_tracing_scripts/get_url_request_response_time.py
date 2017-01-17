from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        request_response_time, request_id, served_from_cache = get_request_response_time(network_filename, page)
        output_to_file(output_dir, page, request_response_time, request_id, served_from_cache)

def output_to_file(output_dir, page, request_response_time, request_id_to_url, served_from_cache):
    sorted_request_response_time = sorted(request_response_time.iteritems(), key=lambda x: x[1][0])
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for request_response_time in sorted_request_response_time:
            request_id = request_response_time[0]
            url = request_id_to_url[request_id]
            if not url.startswith('data:'):
                request_time = -1 if len(request_response_time[1]) < 1 else request_response_time[1][0]
                response_time = -1 if len(request_response_time[1]) < 2 else request_response_time[1][1] 
                fetch_time = -1 if len(request_response_time[1]) < 3 else request_response_time[1][2]
                served_from_cache_str = 'True' if request_id in served_from_cache else 'False'
                output_file.write('{0} {1} {2} {3} {4}\n'.format(url, request_time, response_time, fetch_time, served_from_cache_str))

def get_request_response_time(network_filename, page):
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        result = dict() # Mapping from request_id --> [ request time, response first byte time, finish time ]
        request_id_to_url = dict()
        served_from_cache = set()
        seen_url = set()
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                request_id = network_event['params']['requestId']
                if not found_first_request:
                    if common_module.escape_page(url) == page:
                        found_first_request = True
                    else:
                        continue
                
                timestamp = network_event['params']['timestamp']
                if not url.startswith('data:') \
                        and network_event['params']['request']['method'] == 'GET' \
                        and url not in seen_url:
                    seen_url.add(url)
                    request_id_to_url[request_id] = url
                    result[request_id] = [ timestamp ]

            elif network_event['method'] == 'Network.requestServedFromCache':
                request_id = network_event['params']['requestId']
                if request_id in request_id_to_url:
                    served_from_cache.add(request_id)
                
            elif network_event['method'] == 'Network.responseReceived':
                request_id = network_event['params']['requestId']
                if request_id in result:
                    request_id = network_event['params']['requestId']
                    timestamp = network_event['params']['timestamp']
                    result[request_id].append(timestamp)
                    
                    if network_event['params']['response']['fromDiskCache']:
                        served_from_cache.add(request_id)

            elif network_event['method'] == 'Network.loadingFinished':
                request_id = network_event['params']['requestId']
                if request_id in result:
                    request_id = network_event['params']['requestId']
                    timestamp = network_event['params']['timestamp']
                    result[request_id].append(timestamp)

            elif network_event['method'] == 'Network.loadingFailed':
                request_id = network_event['params']['requestId']
                if request_id in result:
                    request_id = network_event['params']['requestId']
                    timestamp = network_event['params']['timestamp']
                    result[request_id].append(timestamp)

        return result, request_id_to_url, served_from_cache

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
