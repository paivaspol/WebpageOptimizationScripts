from argparse import ArgumentParser

import json

def main(network_filename):
    request_id_to_url = dict()
    request_id_to_type = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                request_id = network_event['params']['requestId']
                request_id_to_url[request_id] = url
            elif network_event['method'] == 'Network.responseReceived':
                request_id = network_event['params']['requestId']
                resource_type = network_event['params']['type']
                request_id_to_type[request_id] = resource_type


    for request_id, url in request_id_to_url.iteritems():
        if request_id in request_id_to_type:
            print('{0} {1}'.format(url, request_id_to_type[request_id]))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    main(args.network_filename)
