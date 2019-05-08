from argparse import ArgumentParser 
from collections import defaultdict

import constants
import common_module
import os
import simplejson as json

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = common_module.get_pages(args.page_list)

    failed_pages = []
    for page in pages:
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(dependency_filename) and os.path.exists(network_filename)):
            failed_pages.append(page)
            continue
        dependencies = common_module.get_dependencies(dependency_filename)
        request_id_to_encoded_size, request_id_to_type, request_id_to_url = get_page_size_stats(page, network_filename, dependencies)
        js_css_html_sizes, page_size, important_resource_count= get_js_css_html_sizes(request_id_to_encoded_size, request_id_to_type)
        if page_size > 0:
            fraction = 1.0 * js_css_html_sizes / page_size
            print '{0} {1} {2} {3} {4}'.format(page, js_css_html_sizes, page_size, fraction, important_resource_count)
            if args.output_resource_size is not None:
                output_resources(request_id_to_encoded_size, request_id_to_url, args.output_resource_size, page)
        else:
            failed_pages.append(page)
    print 'Failed Pages: ' + str(failed_pages)

def output_resources(request_id_to_encoded_size, request_id_to_url, output_directory, page):
    if not os.path.exists(output_directory):
        os.mkdir(output_directory)
    if not os.path.exists(os.path.join(output_directory, page)):
        os.mkdir(os.path.join(output_directory, page))

    output_filename = os.path.join(output_directory, page, 'resource_size.txt')
    with open(output_filename, 'wb') as output_file:
        for request_id in request_id_to_encoded_size:
            url = request_id_to_url[request_id]
            encoded_size = request_id_to_encoded_size[request_id]
            output_file.write('{0} {1}\n'.format(url, encoded_size))

def get_js_css_html_sizes(request_id_to_encoded_size, request_id_to_type):
    js_css_html_size = 0
    important_resource_count = 0
    for request_id in request_id_to_encoded_size:
        resource_type = request_id_to_type[request_id]
        if resource_type == 'Script' or \
            resource_type == 'Stylesheet' or \
            resource_type == 'Document':
            js_css_html_size += request_id_to_encoded_size[request_id]
            important_resource_count += 1
    total_page_size = sum([ x for x in request_id_to_encoded_size.values() if x != -1 ])
    return js_css_html_size, total_page_size, important_resource_count

def get_page_size_stats(page, network_filename, dependencies):
    # print dependencies
    with open(network_filename, 'rb') as input_file:
        request_id_to_encoded_size = dict()
        request_id_to_type = dict()
        request_id_to_url = dict()
        total_page_size = 0
        found_first_request = False
        first_request_timestamp = -1
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
            if network_event[constants.METHOD] == 'Network.responseReceived':
                url = network_event[constants.PARAMS][constants.RESPONSE][constants.URL]
                status = network_event[constants.PARAMS][constants.RESPONSE][constants.STATUS]
                if status == 200:
                    request_id_to_encoded_size[request_id] = -1
                    request_id_to_type[request_id] = network_event[constants.PARAMS][constants.TYPE]
                    request_id_to_url[request_id] = url
            elif network_event[constants.METHOD] == 'Network.loadingFinished':
                if request_id in request_id_to_encoded_size:
                    request_id_to_encoded_size[request_id] = network_event[constants.PARAMS][constants.ENCODED_DATA_LENGTH]
        return request_id_to_encoded_size, request_id_to_type, request_id_to_url


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--output-resource-size', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
