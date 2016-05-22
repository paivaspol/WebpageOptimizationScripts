from argparse import ArgumentParser
from WhoIsDictionary import WhoIsDictionary

import common_module
import os

def process_pages(root_dir):
    whois_org_dict = WhoIsDictionary()
    pages = os.listdir(root_dir)
    counter = 0
    for page in pages:
        print 'Processing: {0} {1}'.format(page, counter)
        populate_whois_dict(root_dir, page, whois_org_dict)
        counter += 1

def populate_whois_dict(root_dir, page, whois_org_dict):
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    if not os.path.exists(request_id_to_url_filename):
        return 
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            domain = common_module.extract_domain(line[1])
            if not whois_org_dict.domain_exists(domain):
                whois_org_dict.get_registrant_for_domain(domain)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_pages(args.root_dir)
