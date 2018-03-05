from argparse import ArgumentParser

import common_module
import json
import numpy
import os
import sys

PARAMS = 'params'
RESPONSE = 'response'
REQUEST = 'request'
URL = 'url'
METHOD = 'method'

def main(root_dir, last_n_days, pages, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    averages = []
    skipped_pages = set()
    for page in pages:
        print 'processing: ' + page
        page = common_module.escape_url(page)
        skip_page = False # Indicator to decide whether to skip processing this page.
        page_common_resources = set()
        request_order = None
        for day in last_n_days:
            print '\tday: ' + day
            run_path = os.path.join(root_dir, day, '0', page)
            network_filename = os.path.join(run_path, 'network_' + page)
            if not os.path.exists(network_filename):
                skip_page = True
                skipped_pages.add(page)
                break
            resources_set, resources_list, resource_type_map = find_all_resources(network_filename, page)
            if request_order is None:
                request_order = resources_list

            if len(page_common_resources) == 0:
                page_common_resources = resources_set
            else:
                page_common_resources = page_common_resources & resources_set

            if not os.path.exists(args.output_dir):
                os.mkdir(args.output_dir)

            prefetch_output_dir = os.path.join(args.output_dir, 'prefetch')
            order_output_dir = os.path.join(args.output_dir, 'order')
            if not os.path.exists(prefetch_output_dir):
                os.mkdir(prefetch_output_dir)
            if not os.path.exists(order_output_dir):
                os.mkdir(order_output_dir)

            prefetch_urls_filename = os.path.join(args.output_dir, 'prefetch', page)
            output_with_resource_type(prefetch_urls_filename, [ x for x in request_order if x in page_common_resources ], resource_type_map)

            order_filename = os.path.join(args.output_dir, 'order', page)
            output(order_filename, request_order,)
    print 'skipped: ' + str(skipped_pages)
                
def output_with_resource_type(output_filename, resource_list, resource_type_map):
    with open(output_filename, 'wb') as output_file:
        lines = []
        for r in resource_list:
            lines.append('{0} {1}'.format(r, resource_type_map[r]))
        output_file.write('\n'.join(lines).strip())

def output(output_filename, resource_list):
    with open(output_filename, 'wb') as output_file:
        output_file.write('\n'.join(resource_list).strip())

def find_all_resources(network_filename, page):
    resource_set = set()
    resource_list = []
    resource_type_map = {}
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            try:
                network_event = json.loads(json.loads(raw_line.strip()))
            except Exception:
                network_event = json.loads(raw_line.strip())
            if not found_first_request and \
                network_event[METHOD] == 'Network.requestWillBeSent':
                if common_module.escape_url(network_event[PARAMS][REQUEST]['url']) == page:
                    found_first_request = True
                url = network_event[PARAMS][REQUEST][URL]
            if not found_first_request:
                continue
            if network_event[METHOD] == 'Network.responseReceived':
                url = network_event[PARAMS][RESPONSE][URL]
                resource_type = network_event[PARAMS]['type']
                if url.startswith('http') and url not in resource_set:
                    if common_module.escape_url(network_event[PARAMS][RESPONSE]['url']) == page or \
                            '.ico' in network_event[PARAMS][RESPONSE]['url']:
                        continue
                    resource_list.append(url)
                    resource_set.add(url)
                    resource_type_map[url] = resource_type
    return resource_set, resource_list, resource_type_map

def get_pages(pages_file):
    '''
    Returns a list of page names.
    '''
    result = []
    with open(pages_file, 'rb') as input_file:
        for raw_line in input_file:
            if not raw_line.startswith("#"):
                line = raw_line.strip().split()
                page = common_module.escape_url(line[len(line) - 1])
                result.append(page)
    return result

def GetLastNDays(root_dir, n_days):
    dirs = [ int(x) for x in os.listdir(root_dir) ]
    dirs.sort()
    return [ str(x) for x in dirs[len(dirs) - n_days:] ]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('prev_days', type=int)
    parser.add_argument('pages_file')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    pages = get_pages(args.pages_file)
    last_n_days = GetLastNDays(args.root_dir, args.prev_days)
    print 'TS considered: ' + str(last_n_days)
    main(args.root_dir, last_n_days, pages, args.output_dir)
