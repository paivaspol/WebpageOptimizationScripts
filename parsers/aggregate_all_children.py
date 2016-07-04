from argparse import ArgumentParser

import common_module
import os

filetypes = [ 'html', 'css' ]

def main(root_dir):
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        page_dir = os.path.join(root_dir, page)
        all_children = set()
        for filetype in filetypes:
            filename = os.path.join(page_dir, filetype + '_children.txt')
            if not os.path.exists(filename):
                continue
            with open(filename, 'rb') as input_file:
                for raw_line in input_file:
                    all_children.add(raw_line.strip())
        output_to_file(all_children, os.path.join(page_dir, 'all_children.txt'))

def output_to_file(all_children, output_filename):
    with open(output_filename, 'wb') as output_file:
        for child in all_children:
            output_file.write(child + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir)
