from argparse import ArgumentParser

import common_module
import os

def get_children_count(root_dir, external_only):
    result = []
    for directory in os.listdir(root_dir):
        children_count_filename = os.path.join(root_dir, directory, 'css_children_count.txt')
        if not os.path.exists(children_count_filename):
            continue
        children_count_dict = common_module.get_css_children_count_dict(children_count_filename)
        if external_only:
            request_to_url_filename = os.path.join(root_dir, directory, 'request_id_to_url.txt')
            if os.path.exists(request_to_url_filename):
                request_to_url = common_module.parse_request_to_url(request_to_url_filename)
                children_count_dict = common_module.remove_non_external_domain(directory, children_count_dict, request_to_url)
            else:
                print 'file not found'

        result.extend(children_count_dict.values())
    result.sort()
    print_results(result)

def print_results(results):
    for result in results:
        print result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--external-only', default=False, action='store_true')
    args = parser.parse_args()
    get_children_count(args.root_dir, args.external_only)
