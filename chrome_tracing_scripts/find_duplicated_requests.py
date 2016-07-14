from argparse import ArgumentParser

import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        if not process_network_trace(network_filename):
            print '{0} has duplicated requests.'.format(page)

def process_network_trace(network_filename):
    with open(network_filename, 'rb') as input_file:
        requested_urls = set()
        request_to_network_event = dict()
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                if url not in requested_urls:
                    requested_urls.add(url)
                    request_to_network_event[url] = network_event
                else:
                    print 'original: ' + str(request_to_network_event[url])
                    print 'duplicated: ' + str(network_event)
                    return False
    return True


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)

