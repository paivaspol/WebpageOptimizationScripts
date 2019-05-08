from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import subprocess

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        inline_css_files = os.listdir(os.path.join(root_dir, page))
        common_module.setup_directory(output_dir, page)
        counter = 0
        for inline_css_file in inline_css_files:
            css_filename = os.path.join(root_dir, page, inline_css_file)
            output_filename = os.path.join(output_dir, page, str(counter))
            cmd = 'node css_parser.js {0} {1}'.format(css_filename, output_filename)
            subprocess.call(cmd, shell=True)
            counter += 1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
