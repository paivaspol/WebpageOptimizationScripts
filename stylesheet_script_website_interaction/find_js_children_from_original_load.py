from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import simplejson as json

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        process_page(root_dir, page)

def process_page(root_dir, page):
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not os.path.exists(network_filename):
        return
    js_children, same_domain_js, external_domain_js, all_requests, _ = common_module.process_network_file(network_filename, page)
    print '{0} {1} {2} {3} {4}'.format(page, len(same_domain_js), len(external_domain_js), len(js_children), len(all_requests))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
