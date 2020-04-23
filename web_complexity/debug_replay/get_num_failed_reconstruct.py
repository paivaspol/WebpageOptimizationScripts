r'''
Outputs the number of resources that could not be reconstructed.
'''
from argparse import ArgumentParser
from urllib.parse import urlparse

import os

def Main():
    for d in os.listdir(args.failed_urls_dir):
        page_dir = os.path.join(args.failed_urls_dir, d)
        failed_count = 0
        for f in os.listdir(page_dir):
            full_path = os.path.join(page_dir, f)
            with open(full_path, 'r') as input_file:
                for l in input_file:
                    parsed_url = urlparse(l.strip())
                    if IsJavaScript(parsed_url.path) or \
                            IsHtml(parsed_url.path) or \
                            IsCss(parsed_url.path):
                        failed_count += 1
        print('{0} {1}'.format(d, failed_count))


def IsJavaScript(path):
    return '.js' in path


def IsHtml(path):
    return path.endswith('.html')


def IsCss(path):
    return path.endswith('.css')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('failed_urls_dir')
    args = parser.parse_args()
    Main()
