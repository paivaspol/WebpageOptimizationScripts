from argparse import ArgumentParser
from urlparse import urlparse

import os
import subprocess

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    counter = 0
    for page in pages:
        counter += 1
        print 'Page: {0} {1}/{2}'.format(page, counter, len(pages))
        page_directory = os.path.join(root_dir, page)
        request_to_url_file = os.path.join(root_dir, page, 'request_id_to_url.txt')
        if not os.path.exists(request_to_url_file):
            continue
        js_file_list = get_js_file_list(request_to_url_file)
        copy_files(page_directory, js_file_list, output_dir, copy_beautified=True)

def get_js_file_list(request_to_url_file):
    '''
    Returns a list containing request ids of javascript files.
    '''
    js_file_list = []
    with open(request_to_url_file, 'rb') as input_file:
        for raw_line in input_file:
            try:
                request_id, url = raw_line.strip().split()
                parsed_url = urlparse(url)
                if parsed_url.path.endswith('.js'):
                    js_file_list.append(request_id)
            except Exception as e:
                pass
    return js_file_list

def copy_files(base_directory, file_list, dst, copy_beautified=False):
    if not os.path.exists(dst):
        os.mkdir(dst)
    for filename in file_list:
        if copy_beautified:
            filename += '.beautified'
        src = os.path.join(base_directory, filename)
        copy_command = 'cp {0} {1}'.format(src, dst)
        subprocess.call(copy_command.split())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
