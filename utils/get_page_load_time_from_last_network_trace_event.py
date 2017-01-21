from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        plt = get_plt(network_filename, page) * 1000.0
        print '{0} {1}'.format(page, plt)

def get_plt(network_filename, page):
    initial_request_time = -1
    latest_timestamp = -1
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            try:
                network_event = json.loads(json.loads(line))
            except:
                network_event = json.loads(line)

            if network_event['method'] == 'Network.requestWillBeSent':
                if initial_request_time == -1 and \
                    common_module.escape_page(network_event['params']['request']['url']) == page:
                    initial_request_time = float(network_event['params']['timestamp'])
            
            elif network_event['method'] == 'Network.loadingFinished':
                latest_timestamp = max(latest_timestamp, float(network_event['params']['timestamp']))
    return latest_timestamp - initial_request_time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
