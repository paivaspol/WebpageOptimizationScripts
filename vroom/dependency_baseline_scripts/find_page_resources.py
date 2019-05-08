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
        if not os.path.exists(network_filename):
            continue
        urls, page_url = find_url_list(network_filename, page)
        output_to_file(page, page_url, urls, output_dir)

def output_to_file(page, page_url, urls, output_dir):
    output_filename = os.path.join(output_dir, page, 'dependency_tree.txt')
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))
    with open(output_filename, 'wb') as output_file:
        for url, url_type in urls.iteritems():
            output_file.write('{0} {1} {2} {3} {4}\n'.format(page_url, 'None', url, -1, url_type))

def find_url_list(network_filename, page):
    seen_urls = set()
    found_first_request = False
    url_to_type = dict()
    page_url = None
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except:
                network_event = json.loads(raw_line.strip())

            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                if not found_first_request:
                    if common_module.escape_page(url) == page:
                        found_first_request = True
                        page_url = url
                    else:
                        continue
                if not url.startswith('data'):
                    seen_urls.add(url)
            elif found_first_request and network_event['method'] == 'Network.responseReceived':
                url = network_event['params']['response']['url']
                if url in seen_urls:
                    resource_type = network_event['params']['type']
                    url_to_type[url] = resource_type
    return url_to_type, page_url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
