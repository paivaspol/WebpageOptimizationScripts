from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)

    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.join(network_filename):
            continue
        html_load_time = process_network_file(network_filename, page)
        print '{0} {1}'.format(page, html_load_time)

def process_network_file(network_filename, page):
    with open(network_filename, 'rb') as input_file:
        first_request_id = None
        request_ts = None
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except:
                network_event = json.loads(raw_line.strip())
            if 'requestId' in network_event['params']:
                request_id = network_event['params']['requestId']
                if network_event['method'] == 'Network.requestWillBeSent':
                    if common_module.escape_page(network_event['params']['request']['url']) == page:
                        first_request_id = request_id
                        request_ts = float(network_event['params']['timestamp'])
                elif network_event['method'] == 'Network.loadingFinished':
                    if request_id == first_request_id:
                        timestamp = float(network_event['params']['timestamp'])
                        html_load_time = timestamp - request_ts
                        return html_load_time
            else:
                print network_event
    return -1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir)
