from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import os
import tldextract

REQUEST_ID_TO_URL_MAP_FILENAME = 'request_id_to_url.txt'

def process_pages(pages, root_dir, print_for_plot):
    for page in pages:
        escaped_page = common_module.escape_page(page)
        site_directory = os.path.join(root_dir, escaped_page, 'response_body')
        request_id_filename = os.path.join(site_directory, \
                                           REQUEST_ID_TO_URL_MAP_FILENAME)
        if not os.path.exists(request_id_filename):
            # Skip.
            continue

        total_resources, external_scripts, external_stylesheets = \
            find_third_party_resources_for_site(page, request_id_filename)
        total_external_resources = sum(external_scripts.values()) + \
                                    sum(external_stylesheets.values())
        if total_resources == 0:
            # Skip.
            continue
        num_external_scripts = sum(external_scripts.values())
        num_external_stylesheets = sum(external_stylesheets.values())
        if print_for_plot:
            print_for_plotting(page, total_resources, num_external_scripts, \
                    num_external_stylesheets)
        else:
            print '# Page total_resources num_external_scripts num_external_stylesheets'
            print_pretty(page, total_resources, num_external_scripts, \
                    num_external_stylesheets)

##################################################################
# Output functions
def print_pretty(page, total_resources, num_external_scripts, num_external_stylesheets):
    total_external_resources = num_external_scripts + num_external_stylesheets
    print 'Page: ' + page + ' Total Resources: ' + str(total_resources)
    print '\tExternal Scripts: ' + str(num_external_scripts)
    print '\tExternal Stylesheets: ' + str(num_external_stylesheets)
    print '\tTotal External Resources: ' + str(total_external_resources)
    print '\tRatio: ' + str(100.0 * total_external_resources / total_resources) + '%'

def print_for_plotting(page, total_resources, num_external_scripts, num_external_stylesheets):
    print '{0} {1} {2} {3}'.format(page, total_resources, \
            num_external_scripts, num_external_stylesheets)

##################################################################
# Find third party stats.
def find_third_party_resources_for_site(page_url, request_id_mapping_filename):
    page_domain = common_module.extract_domain(page_url)
    external_scripts = defaultdict(lambda: 0)
    external_stylesheets = defaultdict(lambda: 0)
    total_resources = 0

    with open(request_id_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            request_id, url = process_line_tokens(raw_line.strip().split())
            url_path = extract_path(url)
            resource_domain = common_module.extract_domain(url)
            total_resources += 1
            if page_domain != resource_domain:
                if url_path.endswith('.js'):
                    # It's a script.
                    external_scripts[resource_domain] += 1
                elif url_path.endswith('.css'):
                    external_stylesheets[resource_domain] += 1
    return total_resources, external_scripts, external_stylesheets

def process_line_tokens(line_tokens):
    url = ''
    for i in range(1, len(line_tokens)):
        url += line_tokens[i]
    return line_tokens[0], url

def extract_path(url):
    parsed_uri = urlparse(url)
    return parsed_uri.path

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_file')
    parser.add_argument('--print-for-plotting', default=False, action='store_true')
    args = parser.parse_args()
    pages = common_module.parse_pages_file(args.pages_file)
    process_pages(pages, args.root_dir, args.print_for_plotting)
