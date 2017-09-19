from argparse import ArgumentParser

import common_module
import os
import simplejson as json

def main(root_dir, page_list_filename, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    page_list = get_page_list(page_list_filename)
    real_page_name = get_real_page_list(page_list_filename)
    pages = os.listdir(root_dir)
    for page in pages:
        print page
        network_event = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_event):
            print network_event + ' not found'
            continue
        try:
            output_page = page if not args.use_redirected_url else page_list[page]
            page_url = real_page_name[page][0] if not args.use_redirected_url else real_page_name[page][1]
            dependency_lines = get_all_requests(page, network_event, page_url)
            output_to_file(output_dir, output_page, dependency_lines)
        except KeyError as e:
            pass

def output_to_file(output_dir, page, dependency_lines):
    if args.output_to_dir:
        if not os.path.exists(os.path.join(output_dir, page)):
            os.mkdir(os.path.join(output_dir, page))
        output_filename = os.path.join(output_dir, page, 'dependency_tree.txt')
    else:
        output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for dependency_line in dependency_lines:
            output_file.write(dependency_line)

def get_all_requests(page, network_event_filename, page_url):
    dependency_lines = []
    request_id_found = set()
    with open(network_event_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] == 'Network.requestWillBeSent':
                request_id = network_event['params']['requestId']
                request_id_found.add(request_id)
            elif network_event['method'] == 'Network.responseReceived':
                request_id = network_event['params']['requestId']
                if request_id in request_id_found:
                    url = network_event['params']['response']['url']
                    resource_type = network_event['params']['type']
                    dependency_line = '{0} None {1} -1 {2}\n'.format(page_url, url, resource_type)
                    if not url.startswith('data'):
                        dependency_lines.append(dependency_line)
    return dependency_lines

def get_page_list(page_list_filename):
    result = dict()
    with open(page_list_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[common_module.escape_page(line[0])] = common_module.escape_page(line[1])
    return result

def get_real_page_list(page_list_filename):
    result = dict()
    with open(page_list_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[common_module.escape_page(line[0])] = (line[0], line[1])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('output_dir')
    parser.add_argument('--use-redirected-url', default=False, action='store_true')
    parser.add_argument('--output-to-dir', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.page_list, args.output_dir)
