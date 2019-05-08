from argparse import ArgumentParser
from bs4 import BeautifulSoup

import common_module
import itertools
import os
import re
import simplejson as json

CSS_TYPE = 'type'
CSS_DOWNLOAD = 'download'
CSS_URL = 'url'
CSS_RULE = 'rule'
CSS_FONTFACE = 'font-face'

URL = 'url\('

NUM_PROCESSES = 4

def main(original_html_filename, css_filename):
    if not os.path.exists(original_html_filename):
        return

    parsed_html = BeautifulSoup(open(original_html_filename), 'html.parser')
    css_children = set()
    with open(css_filename, 'rb') as css_file_obj:
        css_rule_declarations = json.load(css_file_obj)['results']
        for css_rule_declaration in css_rule_declarations:
            if CSS_TYPE not in css_rule_declaration:
                continue

            if css_rule_declaration[CSS_TYPE] == CSS_FONTFACE:
                url = extract_urls_from_fontface_urls(css_rule_declaration[CSS_URL])
                if url is not None:
                    css_children.add(url)
            elif css_rule_declaration[CSS_TYPE] == CSS_RULE:
                # Also handle selector.
                for selector in css_rule_declaration['selectors']:
                    try:
                        result_from_selector = parsed_html.select(selector)
                        if len(result_from_selector) > 0:
                            css_children |= extract_urls_from_css_value(css_rule_declaration[CSS_URL])
                    except (ValueError, NotImplementedError) as e:
                        pass
    output_to_file(css_children)

def output_to_file(css_children):
    for css_child in css_children:
        print css_child.encode('utf8')

def extract_urls_from_css_value(css_value):
    urls = set()
    start_locations = [ m.start() for m in re.finditer(URL, css_value) ]
    for start_location in start_locations:
        counter = start_location
        cur_char = css_value[start_location]
        cur_url = ''
        while cur_char != ')':
            cur_url += cur_char
            counter += 1
            cur_char = css_value[counter]
        cur_url = remove_url_prefix_and_suffix(cur_url)
        if not cur_url.startswith('data'):
            urls.add(cur_url)
    return urls

def extract_urls_from_fontface_urls(css_value):
    urls = set()
    start_locations = [ m.start() for m in re.finditer(URL, css_value) ]
    for start_location in start_locations:
        counter = start_location
        cur_char = css_value[start_location]
        cur_url = ''
        while cur_char != ')':
            cur_url += cur_char
            counter += 1
            cur_char = css_value[counter]
        cur_url = remove_url_prefix_and_suffix(cur_url)
        if not cur_url.startswith('data') and 'woff' in os.path.splitext(cur_url)[1]:
            return cur_url
    return None

def remove_url_prefix_and_suffix(url):
    if url.startswith('url('):
        url = url[len('url('):]
    if url.endswith(')'):
        url = url[:len(url) - 1]
    if url.startswith('"') or url.startswith('\''):
        url = url[1:]
    if url.endswith('"') or url.endswith('\''):
        url = url[:len(url) - 1]
    return url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('html_filename')
    parser.add_argument('css_filename')
    args = parser.parse_args()
    main(args.html_filename, args.css_filename)
