from argparse import ArgumentParser
from collections import defaultdict
from multiprocessing import Pool, freeze_support

import common_module
import itertools
import os

DIRECTORY = 'apple-pi.eecs.umich.edu_grouped_domain_script_execution_{0}_{1}.html'

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        process_page(root_dir, page)

def process_page(root_dir, page):
    page_directory = page
    if args.use_custom_page:
        index = 0
        page_directory = DIRECTORY.format(page, index)
        page_path = os.path.join(root_dir, page_directory)
        while os.path.exists(page_path):
            print 'page: ' + page_directory
            network_filename = os.path.join(root_dir, page_directory, 'network_' + page_directory)
            children_from_js, _, _, all_requests, request_to_url_dict = common_module.process_network_file(network_filename, page_directory)
            for child in children_from_js:
                print '\t{0} {1}'.format(child, request_to_url_dict[child])
            index += 1
            page_directory = DIRECTORY.format(page, index)
            page_path = os.path.join(root_dir, page_directory)
    else:
        network_filename = os.path.join(root_dir, page_directory, 'network_' + page)
        if not os.path.exists(network_filename):
            return
        children_from_js, _, _, all_requests, request_to_url_dict = common_module.process_network_file(network_filename, page)
        resource_breakdown = get_resource_type_breakdown(children_from_js, request_to_url_dict)
        # for resource_type in resource_breakdown:
        #     print '\t{0} {1}'.format(resource_type, resource_breakdown[resource_type])
        total_js_resource = sum([ len(x) for _, x in resource_breakdown.iteritems() ])
        print '{0} {1} {2} {3} {4} {5}'.format(page, len(resource_breakdown['.html']), len(resource_breakdown['.css']), \
                                    len(resource_breakdown['.js']), total_js_resource, len(all_requests))
        # for child in children_from_js:
        #     print '{0} {1}'.format(child, request_to_url_dict[child])


def get_resource_type_breakdown(children_from_js, request_to_url_dict):
    result = defaultdict(set)
    for child in children_from_js:
        if '.html' in request_to_url_dict[child]:
            result['.html'].add(request_to_url_dict[child])
        elif '.js?' in request_to_url_dict[child] or request_to_url_dict[child].endswith('.js'):
            result['.js'].add(request_to_url_dict[child])
        elif '.css' in request_to_url_dict[child]:
            result['.css'].add(request_to_url_dict[child])
        else:
            pass
            # print request_to_url_dict[child]
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--page', default=None)
    parser.add_argument('--use-custom-page', default=False, action='store_true')
    args = parser.parse_args()
    if args.page is not None:
        process_page(args.root_dir, args.page)
    else:
        process_pages(args.root_dir)
