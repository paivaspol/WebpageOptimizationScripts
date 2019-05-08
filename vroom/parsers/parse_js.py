from argparse import ArgumentParser
from urlparse import urlparse
from multiprocessing import Pool, freeze_support

import common_module
import os
import subprocess
import itertools

NUM_PROCESSES = 4

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    common_module.create_directory_if_not_exists(output_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(process_page_wrapper,\
                    itertools.izip(pages, \
                    itertools.repeat(root_dir), \
                    itertools.repeat(output_dir)))

def process_page_wrapper(args):
    return process_page(*args)

def process_page(page, root_dir, output_dir):
    request_id_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    if not os.path.exists(request_id_filename):
        return
    common_module.setup_directory(output_dir, page)
    mapping_filename = os.path.join(output_dir, page, 'filename_to_request_id_mapping.txt')
    if os.path.exists(mapping_filename):
        os.rm(mapping_filename)
    with open(request_id_filename, 'rb') as input_file:
        counter = 0
        for raw_line in input_file:
            line = raw_line.strip().split()
            request_id = line[0]
            url = line[1]
            parsed_url = urlparse(url)
            if parsed_url.path.endswith('.js'):
                css_filename = os.path.join(root_dir, page, request_id + '.beautified')
                output_filename = os.path.join(output_dir, page, str(counter))
                cmd = 'node js_parser.js {0} {1}'.format(css_filename, output_filename)
                subprocess.call(cmd, shell=True)
                output_filename_to_url_mapping(os.path.join(output_dir, page), request_id, url, str(counter))
                counter += 1
                

def output_filename_to_url_mapping(page_output_dir, request_id, url, filename):
    with open(os.path.join(page_output_dir, 'filename_to_request_id_mapping.txt'), 'ab') as output_file:
        output_file.write('{0} {1} {2}\n'.format(filename, request_id, url))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
