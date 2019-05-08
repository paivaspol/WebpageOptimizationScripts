from argparse import ArgumentParser

import common_module
import os

def process_websites(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for directory in pages:
        base_dir = os.path.join(root_dir, directory)
        css_children_filename = os.path.join(base_dir, 'css_children_count.txt')
        if not os.path.exists(css_children_filename):
            continue
        css_count_dict = common_module.get_css_children_count_dict(css_children_filename)
        if args.external_only or args.internal_only:
            request_to_url_filename = os.path.join(base_dir, 'request_id_to_url.txt')
            if not os.path.exists(request_to_url_filename):
                print 'here: ' + request_to_url_filename
                continue
            request_id_to_url = common_module.parse_request_to_url(request_to_url_filename)
            if args.external_only:
                css_count_dict = common_module.remove_non_external_domain(directory, css_count_dict, request_id_to_url)
            elif args.internal_only:
                css_count_dict = common_module.remove_external_domain(directory, css_count_dict, request_id_to_url)
        num_children_before = sum(x[1] for x in css_count_dict.values())
        num_children_after = sum(x[2] for x in css_count_dict.values())
        num_children_diff = sum(x[3] for x in css_count_dict.values())
        print '{0} {1} {2} {3}'.format(directory, num_children_before, num_children_after, num_children_diff)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--external-only', default=False, action='store_true')
    parser.add_argument('--internal-only', default=False, action='store_true')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_websites(args.root_dir)
