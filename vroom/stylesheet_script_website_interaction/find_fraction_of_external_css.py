from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os

def process_files(root_dir):
    external_css_count = 0
    total_css_count = 0
    for directory in os.listdir(root_dir):
        page_external_css_count = 0
        page_total_css_count = 0
        request_to_url_mapping_filename = os.path.join(root_dir, directory, 'request_id_to_url.txt')
        if not os.path.exists(request_to_url_mapping_filename):
            continue
        with open(request_to_url_mapping_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                parsed_url = urlparse(line[1])
                if parsed_url.path.endswith('.css'):
                    domain = common_module.extract_domain(line[1])
                    if domain != directory:
                        page_external_css_count += 1
                    page_total_css_count += 1
            if page_total_css_count > 0:
                page_fraction_of_external_css = 1.0 * page_external_css_count / page_total_css_count
                print '{0} {1} {2} {3}'.format(directory, page_external_css_count, page_total_css_count, page_fraction_of_external_css) 
                external_css_count += page_external_css_count
                total_css_count += page_total_css_count
    fraction_of_external_css = 1.0 * external_css_count / total_css_count
    print 'total {0} {1} {2}'.format(external_css_count, total_css_count, fraction_of_external_css)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    process_files(args.root_dir)
