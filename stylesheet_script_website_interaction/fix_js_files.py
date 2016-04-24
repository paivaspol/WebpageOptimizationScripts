from argparse import ArgumentParser
from urlparse import urlparse
from collections import defaultdict

import common_module
import os
import re

def process_directories(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages:
        pages = get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    escaped_chars = defaultdict(lambda: 0)
    for page in pages:
        if page != 'firefox.com':
            continue

        # print 'Processing: ' + page
        current_dir = os.path.join(root_dir, page)
        request_id_to_url_filename = os.path.join(root_dir, page, 'response_body', 'request_id_to_url.txt')
        if not os.path.exists(request_id_to_url_filename):
            continue
        page_output_dir = os.path.join(output_dir, page)
        page_escaped_chars = fix_javascripts(current_dir, request_id_to_url_filename, page_output_dir)
        for escaped in page_escaped_chars:
            escaped_chars[escaped] += page_escaped_chars[escaped]
    print_all_escaped_characters(escaped_chars)

def fix_javascripts(current_dir, request_id_to_url_filename, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    all_unique_escaped_characters = defaultdict(lambda: 0)
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parsed_url = urlparse(line[1])
            if '.js' in parsed_url.path:
                js_filename = os.path.join(current_dir, 'response_body', line[0])
                if os.path.exists(js_filename):
                    js_string = get_javascript_str(js_filename)
                    histogram = get_all_escaped_characters(js_string)
                    for entry in histogram:
                        all_unique_escaped_characters[entry] += histogram[entry]
                    output_filename = os.path.join(output_dir, line[0])
                    fixed_js = replace_escaped_html_characters_with_actual_characters(js_string)
                    write_result(fixed_js, output_filename)


    return all_unique_escaped_characters

def write_result(fixed_js, output_filename):
    with open(output_filename, 'wb') as output_file:
        output_file.write(fixed_js)

def print_all_escaped_characters(all_unique_escaped_characters):
    sorted_histogram = sorted(all_unique_escaped_characters.iteritems(), key=lambda x: x[1], reverse=True)
    for escaped_char in sorted_histogram:
        print escaped_char[0] + ' ' + str(escaped_char[1])

def get_all_escaped_characters(js_string):
    matched_strings = re.findall('&[a-zA-Z0-9]+;', js_string)
    result = defaultdict(lambda: 0)
    for matched in matched_strings:
        result[matched] += 1
    return result

def replace_escaped_html_characters_with_actual_characters(js_string):
    html_code_dict = { \
            '&quot;': '"', \
            '&lt;': '<', \
            '&gt;': '>', \
            '&amp;': '&'
    }
    removed_extra_semicolon_js = js_string
    cur_token = ''
    start_pos = -1
    i = 0
    while i < len(removed_extra_semicolon_js):
        c = removed_extra_semicolon_js[i]
        if c == '&':
            cur_token += c
            start_token = i
        elif cur_token != '':
            cur_token += c
            if c == ';':
                end_token = i
                if cur_token in html_code_dict:
                    removed_extra_semicolon_js = removed_extra_semicolon_js[:start_token] + html_code_dict[cur_token] + removed_extra_semicolon_js[end_token + 1:]
                    i = start_token + len(html_code_dict[cur_token])
                    if removed_extra_semicolon_js[i] != '&':
                        # Not a start of a new token. Find the next ; and remove it.
                        cur_index = i
                        while cur_index < len(removed_extra_semicolon_js):
                            if removed_extra_semicolon_js[cur_index] == ';':
                                semicolon_index = cur_index
                                removed_extra_semicolon_js = removed_extra_semicolon_js[:semicolon_index] + ' ' + removed_extra_semicolon_js[semicolon_index + 1:]
                                i = semicolon_index + 1
                                break
                            cur_index += 1
                    cur_token = ''
                    continue
                cur_token = ''
        i += 1
    return removed_extra_semicolon_js


def get_javascript_str(javascript_filename):
    javascript_str = ''
    with open(javascript_filename, 'rb') as input_file:
        for raw_line in input_file:
            javascript_str += raw_line
    return javascript_str

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    process_directories(args.root_dir, args.output_dir)
