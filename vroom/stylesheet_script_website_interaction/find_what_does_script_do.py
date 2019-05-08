from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import os
import tldextract
import jsbeautifier

REQUEST_ID_TO_URL_MAP_FILENAME = 'request_id_to_url.txt'

def process_pages(pages, root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    for page in pages:
        escaped_page = common_module.escape_page(page)
        page_output_filename = os.path.join(output_dir, escaped_page)
        site_directory = os.path.join(root_dir, escaped_page, 'response_body')
        request_id_filename = os.path.join(site_directory, \
                                           REQUEST_ID_TO_URL_MAP_FILENAME)
        if not os.path.exists(request_id_filename):
            # Skip.
            continue

        scripts = find_third_party_scripts_for_site(page, request_id_filename)
        if len(scripts) == 0:
            # Skip.
            continue
        code_snippets = find_dom_access(scripts, site_directory)
        write_code_snippets(page_output_filename, code_snippets)

##################################################################
# Write code snippets
def write_code_snippets(output_filename, snippets):
    with open(output_filename, 'wb') as output_file:
        output_file.write('Total snippets: ' + str(len(snippets)) + '\n')
        output_file.write('###################################################\n')
        for request_id, url, snippet in snippets:
            output_file.write(str(request_id) + ' ' + url)
            output_file.write(snippet + '\n\n')

##################################################################
# Find DOM Tree access
GET_ELEMENT_BY_ID = 'getElementById'
GET_ELEMENT_BY_NAME = 'getElementByName'

def find_dom_access(request_ids, site_directory):
    snippet = []
    for request_id, url in request_ids:
        full_filename = os.path.join(site_directory, request_id)
        with open(full_filename, 'rb') as input_file:
            for line in input_file:
                if accessing_dom(line):
                    snippet.append((request_id, url, jsbeautifier.beautify(line)))
    return snippet

def accessing_dom(javascript_code):
    '''
    Being a little conservative here. Technically, .innerHTML can also
    introduce DOM Tree access. However, this can also be used when
    creating a new element.
    '''
    return GET_ELEMENT_BY_ID in javascript_code or \
            GET_ELEMENT_BY_NAME in javascript_code

##################################################################
# Find third party resources
def find_third_party_scripts_for_site(page_url, request_id_mapping_filename):
    page_domain = extract_domain(page_url)
    scripts = []
    with open(request_id_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            request_id, url = process_line_tokens(raw_line.strip().split())
            url_path = extract_path(url)
            resource_domain = extract_domain(url)
            if page_domain != resource_domain:
                if url_path.endswith('.js'):
                    # It's a script.
                    scripts.append((request_id, url))
    return scripts

def process_line_tokens(line_tokens):
    url = ''
    for i in range(1, len(line_tokens)):
        url += line_tokens[i]
    return line_tokens[0], url

def extract_domain(url):
    parsed_uri = tldextract.extract(url)
    return parsed_uri.domain + '.' + parsed_uri.suffix

def extract_path(url):
    parsed_uri = urlparse(url)
    return parsed_uri.path

def parse_pages_file(pages_filename):
    pages = []
    with open(pages_filename, 'rb') as input_file:
        for raw_line in input_file:
            pages.append(raw_line.strip())
    return pages

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_file')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    pages = parse_pages_file(args.pages_file)
    process_pages(pages, args.root_dir, args.output_dir)
