from argparse import ArgumentParser
from collections import defaultdict

import common_module
import os

def main(root_dir, num_iterations, pages):
    chromium_logs_missing = defaultdict(list)
    for i in range(0, num_iterations):
        for page in pages:
            page = common_module.escape_url(page)
            path = os.path.join(root_dir, str(i), page)
            files = os.listdir(path)
            if not 'chromium_log.txt' in files:
                chromium_logs_missing[page].append(i)

    for page, missing_chromium_logs in chromium_logs_missing.iteritems():
        print '{0} {1} {2}'.format(page, len(missing_chromium_logs), missing_chromium_logs)

def get_pages(pages_filename):
    with open(pages_filename, 'rb') as input_file:
        return [ line.strip() for line in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('num_iterations', type=int)
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    pages = get_pages(args.pages_filename)
    main(args.root_dir, args.num_iterations, pages)
    
