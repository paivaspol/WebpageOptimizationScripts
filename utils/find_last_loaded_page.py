from argparse import ArgumentParser

import common_module
import os

def find_first_not_loaded_page(downloaded_pages, pages):
    for page in pages:
        if page not in downloaded_pages:
            print pages[page]

def get_downloaded_pages(download_directory):
    downloaded_pages = set(os.listdir(download_directory))
    return downloaded_pages

def parse_pages_file(pages_filename):
    pages = dict()
    with open(pages_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            pages[common_module.escape_page(line[len(line) - 1])] = line[0]
    return pages

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('download_directory')
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    downloaded_pages = get_downloaded_pages(args.download_directory)
    pages = parse_pages_file(args.pages_filename)
    find_first_not_loaded_page(downloaded_pages, pages)
