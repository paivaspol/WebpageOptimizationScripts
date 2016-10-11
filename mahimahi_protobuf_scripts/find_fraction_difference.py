from argparse import ArgumentParser

import os
import subprocess

def main(base_timestamp, compare_timestamp):
    base_urls = get_urls(base_timestamp)
    compare_urls = get_urls(compare_timestamp)
    for page in base_urls:
        if page in compare_urls:
            base_page_urls = base_urls[page]
            compare_page_urls = compare_urls[page]
            # print base_page_urls
            # print compare_page_urls
            url_diff = base_page_urls - compare_page_urls
            fraction = 1.0 * len(url_diff) / len(base_page_urls)
            print '{0} {1}'.format(page, fraction)

def get_urls(directory):
    result = dict()
    pages = os.listdir(directory)
    for page in pages:
        # if 'nih.gov' not in page:
        #     continue
        if page == 'start' or page == 'hars':
            continue
        result[page] = set()
        page_directory = os.path.join(directory, page)
        command = 'python /Users/vaspol/Documents/research/MobileWebPageOptimization/scripts/mahimahi_protobuf_scripts/get_url_list.py {0}'.format(page_directory)
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        lines = out.strip().split()
        for url in lines:
            result[page].add(url.strip())
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('base_directory')
    parser.add_argument('compare_directory')
    args = parser.parse_args()
    main(args.base_directory, args.compare_directory)
