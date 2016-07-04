from argparse import ArgumentParser
from bs4 import BeautifulSoup

import bs4
import common_module
import os

def main(root_dir, output_dir):
    common_module.create_directory_if_not_exists(output_dir)
    pages = os.listdir(root_dir)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        parse_html(page, root_dir, output_dir)

def parse_html(page, root_dir, output_dir):
    print 'processing: ' + page
    page_output_dir = os.path.join(output_dir, page)
    common_module.create_directory_if_not_exists(page_output_dir)
    descendants = set()
    html_filename = os.path.join(root_dir, page, 'before_page_load.html')
    if not os.path.exists(html_filename):
        return

    with open(html_filename, 'rb') as input_file:
        parsed_html = BeautifulSoup(input_file, 'html.parser')
        for i, descendant in enumerate(parsed_html.descendants):
            if type(descendant) is bs4.element.Tag and \
                descendant.name == 'style' and \
                'href' not in descendant.attrs:
                    # Need to parse the CSS and get children from the css.
                    css_str = descendant.string
                    output_to_file(page_output_dir, i, css_str)

def output_to_file(output_dir, css_id, css_str):
    full_path = os.path.join(output_dir, str(css_id))
    with open(full_path, 'wb') as output_file:
        output_file.write(css_str.encode('utf8'))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
