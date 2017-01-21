from argparse import ArgumentParser

import constants
import os
import simplejson as json

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        # if 'sbnation.com' not in page:
        #     continue
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        failed_urls = get_failed_requests(network_filename)
        output_to_file(output_dir, page, failed_urls)

def output_to_file(output_dir, page, urls):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for url in urls:
            output_file.write(url + '\n')

def get_failed_requests(network_filename):
    failed_requests = set()
    request_id_to_url = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == constants.NET_REQUEST_WILL_BE_SENT:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                request_id_to_url[request_id] = url
            elif network_event[constants.METHOD] == constants.NET_LOADING_FAILED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in request_id_to_url and network_event[constants.PARAMS]['errorText'] == 'net::ERR_INTERNET_DISCONNECTED':
                    url = request_id_to_url[request_id]
                    failed_requests.add(url)
    return failed_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
