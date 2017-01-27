from argparse import ArgumentParser
from collections import defaultdict

import common_module
import constants
import os
import simplejson as json

def main(root_dirs, iterations, page_list_filename, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = common_module.get_pages(page_list_filename)
    page_to_failed_urls = defaultdict(set)
    for root_dir in root_dirs:
        for page in pages:
            for i in range(0, iterations):
                # if 'sbnation.com' not in page:
                #     continue
                network_filename = os.path.join(root_dir, str(i), page, 'network_' + page)
                if not os.path.exists(network_filename):
                    continue
                page_to_failed_urls[page].update(get_failed_requests(network_filename))
    for page, failed_urls in page_to_failed_urls.iteritems():
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
                # if request_id in request_id_to_url:
                #     print network_event[constants.PARAMS]['errorText']
                    url = request_id_to_url[request_id]
                    failed_requests.add(url)
    return failed_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir', nargs='+')
    parser.add_argument('iterations', type=int)
    parser.add_argument('page_list')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.iterations, args.page_list, args.output_dir)
