from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import subprocess

def process_directories(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    common_module.remove_file_if_exists(os.path.join(output_dir, 'summary.txt'))
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    found_first_page = False
    for page in pages:
        if not found_first_page and args.first_page is not None and page != args.first_page:
            continue
        else:
            found_first_page = True
        current_dir = os.path.join(root_dir, page)
        request_id_to_url_filename = os.path.join(root_dir, page, 'response_body', 'request_id_to_url.txt')
        if not os.path.exists(request_id_to_url_filename):
            continue
        page_output_dir = os.path.join(output_dir, page)
        html_files, num_failed_download_scripts, total_js = generate_html_files(request_id_to_url_filename, current_dir, page_output_dir)
        print_html_files(args.prefix, page, html_files)
        print_summary_file(output_dir, page, num_failed_download_scripts, total_js)

def print_summary_file(output_dir, page, num_failed_download_scripts, total_js):
    summary_filename = os.path.join(output_dir, 'summary.txt')
    with open(summary_filename, 'ab') as output_file:
        output_file.write('{0} {1} {2}\n'.format(page, num_failed_download_scripts, total_js))

def print_html_files(prefix, page, html_files):
    for html_file in html_files:
        final_url = os.path.join(prefix, page, html_file)
        print final_url

def generate_html_files_with_grouped_js(request_id_to_url_filename, current_dir, output_dir):
    result_pages = []
    common_module.create_directory_if_not_exists(output_dir)
    domain_to_scripts = dict()
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parsed_url = urlparse(line[1])
            if '.js' in parsed_url.path:
                js_name = line[0]

def generate_html_files(request_id_to_url_filename, current_dir, output_dir):
    result_pages = []
    failed_scripts = 0
    total_js = 0
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
                    returncode = wget_js_file(line[1], js_name, output_dir)
                    if returncode == 0:
                        html_filename = write_html_to_file(html_str, js_name, output_dir)
                        result_pages.append(html_filename)
                    else:
                        failed_scripts += 1
                    total_js += 1
                    # copy_js_file(js_name, current_dir, output_dir),
    return result_pages, failed_scripts, total_js

def copy_js_file(js_name, current_dir, output_dir):
    src = os.path.join(current_dir, 'response_body', js_name)
    destination = os.path.join(output_dir, js_name)
    command = 'cp {0} {1}'.format(src, destination)
    subprocess.call(command, shell=True)

def wget_js_file(js_url, js_name, output_dir):
    destination = os.path.join(output_dir, js_name)
    wget_command = 'wget "{0}" -O {1} -q'.format(js_url, destination)
    proc = subprocess.Popen(wget_command, shell=True)
    proc.wait()
    return proc.returncode

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
    parser.add_argument('--first-page', default=None)
    parser.add_argument('--group-same-domain', default=False, action='store_true')
    args = parser.parse_args()
    process_directories(args.root_dir, args.output_dir)
