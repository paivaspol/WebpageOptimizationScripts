from argparse import ArgumentParser

import common_module
import os
import subprocess

def generate_html(root_dir, pages, output_dir, url_prefix):
    for page in pages:
        path = os.path.join(root_dir, page)
        url_output_dir = create_output_dir(output_dir, page.replace('?', '_'))
        resource_sizes_full_path = os.path.join(path, 'request_sizes.txt')
        command = 'python generate_html_with_individual_objects.py {0} {1}'.format(resource_sizes_full_path, \
                                                                                   url_output_dir)
        subprocess.call(command, shell=True)
        print os.path.join(url_prefix, url_output_dir)

def create_output_dir(output_dir, url):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    url_path = os.path.join(output_dir, url)
    if not os.path.exists(url_path):
        os.mkdir(url_path)
    return url_path

def parse_pages(page_list_filename):
    pages = []
    with open(page_list_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            pages.append(common_module.escape_page(line[len(line) - 1]))
    return pages

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--url-prefix', default='')
    args = parser.parse_args()
    pages = parse_pages(args.page_list)
    generate_html(args.root_dir, pages, args.output_dir, args.url_prefix)
