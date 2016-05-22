from argparse import ArgumentParser

import common_module
import os

DIRECTORY = 'apple-pi.eecs.umich.edu_grouped_domain_script_execution_{0}_{1}.html'

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
        print 'page: ' + page
        network_filename = os.path.join(root_dir, page_directory, 'network_' + page)
        children_from_js, _, _, all_requests, request_to_url_dict = common_module.process_network_file(network_filename, page)
        for child in children_from_js:
            print '{0} {1}'.format(child, request_to_url_dict[child])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page')
    parser.add_argument('--use-custom-page', default=False, action='store_true')
    args = parser.parse_args()
    process_page(args.root_dir, args.page)
