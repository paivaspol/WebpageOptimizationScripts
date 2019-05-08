from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import subprocess
import time

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        request_id_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
        if not os.path.exists(request_id_filename):
            continue
        common_module.setup_directory(output_dir, page)
        with open(request_id_filename, 'rb') as input_file:
            counter = 0
            if args.profile_time:
                css_parsing_filename = os.path.join(output_dir, page, 'css_parsing_runtime.txt')
                if os.path.exists(css_parsing_filename):
                    os.remove(css_parsing_filename)

            for raw_line in input_file:
                line = raw_line.strip().split()
                request_id = line[0]
                url = line[1]
                parsed_url = urlparse(url)
                if parsed_url.path.endswith('.css'):
                    css_filename = os.path.join(root_dir, page, request_id + '.beautified')
                    output_filename = os.path.join(output_dir, page, str(counter))
                    cmd = 'node css_parser.js {0} {1}'.format(css_filename, output_filename)
                    start_time = time.time()
                    subprocess.call(cmd, shell=True)
                    end_time = time.time()
                    if args.profile_time:
                        output_timing(os.path.join(output_dir, page), end_time - start_time)
                    counter += 1

def output_timing(output_dir, timing):
    with open(os.path.join(output_dir, 'css_parsing_runtime.txt'), 'ab') as output_file:
        output_file.write(str(timing * 1000) + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--profile-time', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
