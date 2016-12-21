from argparse import ArgumentParser

import common_module
import simplejson as json
import os

def get_request_sizes(network_filename, page, dependencies):
    request_size = dict()
    request_id_to_url = dict()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if not found_first_request:
                if network_event['method'] == 'Network.requestWillBeSent' and \
                    common_module.escape_page(network_event['params']['request']['url']) == page:
                    found_first_request = True
                else:
                    continue
            
            request_id = network_event['params']['requestId']
            if network_event['method'] == 'Network.requestWillBeSent':
                request_size[request_id] = 0
                request_id_to_url[request_id] = network_event['params']['request']['url']
            elif network_event['method'] == 'Network.dataReceived':
                if request_id in request_size:
                    request_size[request_id] += network_event['params']['encodedDataLength']
            elif network_event['method'] == 'Network.loadingFinished':
                request_id = network_event['params']['requestId']
                if request_id in request_size:
                    cumulative_size = request_size[request_id]
                    request_size[request_id] = (max(network_event['params']['encodedDataLength'], cumulative_size), request_id_to_url[request_id])
    request_size = { k: v for (k, v) in request_size.iteritems() if not isinstance(v, int) and v[1] in dependencies }
    return request_size

def get_request_sizes_in_directory(root_dir, dependency_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        full_path = os.path.join(path, 'network_' + url)
        dependency_filename = os.path.join(dependency_dir, url, 'dependency_tree.txt')
        if not os.path.exists(full_path) or not os.path.exists(dependency_filename):
            continue
        dependencies = get_dependencies(dependency_filename)
        page_request_sizes = get_request_sizes(full_path, url, dependencies)
        page_request_size_values = [ size[0] for size in page_request_sizes.values() ]
        print '{0} {1}'.format(url, sum(page_request_size_values))

def get_dependencies(dependency_filename):
    dependencies = set()
    with open(dependency_filename,'rb') as input_file:
        for raw_line in input_file:
            dependencies.add(raw_line.strip().split()[2])
    return dependencies

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    get_request_sizes_in_directory(args.root_dir, args.dependency_dir)
