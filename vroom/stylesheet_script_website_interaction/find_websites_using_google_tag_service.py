from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    use_service = 0
    total_pages = 0
    for page in pages:
        result = process_page(root_dir, page)
        if result is not None:
            if result:
                use_service += 1
                print page
            total_pages += 1
    print '{0} {1} {2}'.format(args.domain, use_service, total_pages)

def process_page(root_dir, page):
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    if not os.path.exists(request_id_to_url_filename):
        return
    request_id_to_url = common_module.parse_request_to_url(request_id_to_url_filename)
    num_hosted_in_external_domain = 0
    total = 0
    for request_id, url in request_id_to_url.iteritems():
        parsed_url = urlparse(url)
        if args.domain in url and '.js' in parsed_url.path:
            return True
    return False

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('domain')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
