from argparse import ArgumentParser

import collections
import os

HTTPS_PREFIX = 'https://'
HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'

def main(root_dir):
    all_urls = get_all_urls_from_all_files(root_dir)
    for url in all_urls:
        print url.split()[0]
    # print 'All URLs:\t' + str(len(all_urls))

def get_all_urls_from_all_files(root_dir):
    result_urls = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        for filename in filenames:
            full_path = os.path.join(path, filename)
            with open(full_path, 'rb') as input_file:
                for line in input_file:
                    result_urls.append(line)
    return result_urls

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)

