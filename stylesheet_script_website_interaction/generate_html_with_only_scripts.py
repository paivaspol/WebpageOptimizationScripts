from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import subprocess

def process_directories(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        current_dir = os.path.join(root_dir, page)
        request_id_to_url_filename = os.path.join(root_dir, page, 'response_body', 'request_id_to_url.txt')
        if not os.path.exists(request_id_to_url_filename):
            continue
        page_output_dir = os.path.join(output_dir, page)
        html_files = generate_html_files(request_id_to_url_filename, current_dir, page_output_dir)
        print_html_files(args.prefix, page, html_files)

def print_html_files(prefix, page, html_files):
    for html_file in html_files:
        final_url = os.path.join(prefix, page, html_file)
        print final_url

def generate_html_files(request_id_to_url_filename, current_dir, output_dir):
    result_pages = []
    common_module.create_directory_if_not_exists(output_dir)
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parsed_url = urlparse(line[1])
            if '.js' in parsed_url.path:
                js_name = line[0]
                original_js_file = os.path.join(current_dir, 'response_body', js_name)
                if os.path.exists(original_js_file):
                    html_str = generate_html_for_page(js_name)
                    html_filename = write_html_to_file(html_str, js_name, output_dir)
                    result_pages.append(html_filename)
                    copy_js_file(js_name, current_dir, output_dir)
    return result_pages

def copy_js_file(js_name, current_dir, output_dir):
    src = os.path.join(current_dir, 'response_body', js_name)
    destination = os.path.join(output_dir, js_name)
    command = 'cp {0} {1}'.format(src, destination)
    subprocess.call(command, shell=True)

def write_html_to_file(html_str, js_name, output_dir):
    html_filename = js_name + '.html'
    output_filename = os.path.join(output_dir, js_name + '.html')
    with open(output_filename, 'wb') as output_file:
        output_file.write(html_str)
    return html_filename

def generate_html_for_page(js_name):
    script_tag = '<script src="{0}"></script>'.format(js_name)
    return get_html_prefix() + script_tag + get_html_suffix()

def get_html_prefix():
    return '<html><head></head><body>'

def get_html_suffix():
    return '<body></body></html>'
    

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--prefix', default='')
    args = parser.parse_args()
    process_directories(args.root_dir, args.output_dir)
