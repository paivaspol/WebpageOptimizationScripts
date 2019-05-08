from argparse import ArgumentParser
from bs4 import BeautifulSoup
from urlparse import urlparse

import common_module
import os

def process_directories(root_dir):
    pages_to_ignore = []
    for directory in os.listdir(root_dir):
        before_page_load_filename = os.path.join(root_dir, directory, 'before_page_load.html')
        if not os.path.exists(before_page_load_filename):
            pages_to_ignore.append(directory)
            continue

        if find_404_in_page(before_page_load_filename):
            request_id_to_url_filename = os.path.join(root_dir, directory, 'request_id_to_url.txt')
            if os.path.exists(request_id_to_url_filename):
                request_id = find_index(request_id_to_url_filename, directory)
                if request_id is not None:
                    print directory + ' ' + request_id
            pages_to_ignore.append(directory)
        # dom_tree_object = get_page_tree_object(before_page_load_filename)
    output_filename = os.path.join('.', 'pages_to_ignore.txt')
    write_pages_to_ignore(output_filename, pages_to_ignore)

def write_pages_to_ignore(filename, pages_to_ignore):
    with open(filename, 'wb') as output_file:
        for page in pages_to_ignore:
            output_file.write(page + '\n')

def find_index(request_id_to_url_filename, directory):
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            parsed_url = urlparse(line[1])
            if directory == common_module.extract_domain(line[1]) and parsed_url.path.endswith('/'):
                print line[1]
                return line[0] 
        return None

def find_404_in_page(html_filename):
    with open(html_filename, 'rb') as input_file:
        in_title = False
        for raw_line in input_file:
            line = raw_line.strip()
            if line == '<title>':
                in_title = True
            elif in_title and line == '404 Not Found':
                return True
            elif line == '</title>':
                in_title = False
            elif line == '</head>':
                break
        return False

def get_page_tree_object(html_filename):
    return BeautifulSoup(open(html_filename), 'html.parser')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    process_directories(args.root_dir)
