from argparse import ArgumentParser

import common_module
import os
from WhoIsDictionary import WhoIsDictionary

def process_pages(root_dir):
    pages = os.listdir(root_dir)
    whois_dictionary = WhoIsDictionary()
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(args.ignore_pages)
    for page in pages:
        process_page(root_dir, page, whois_dictionary)

def process_page(root_dir, page, whois_dictionary):
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    if not os.path.exists(request_id_to_url_filename):
        return
    with open(request_id_to_url_filename, 'rb') as input_file:
        same_domain_js = 0
        all_js = 0
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) == 2:
                request_id, url = line
                if '.js' in url:
                    domain = common_module.extract_domain(url)
                    if whois_dictionary.domain_exists(page) and \
                        whois_dictionary.domain_exists(domain) and \
                        (whois_dictionary.get_registrant_for_domain(domain) == \
                        whois_dictionary.get_registrant_for_domain(page)):
                        same_domain_js += 1
                    all_js += 1
    if all_js > 0:
        fraction = 1.0 * same_domain_js / all_js
        print '{0} {1} {2} {3}'.format(page, same_domain_js, all_js, fraction)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
