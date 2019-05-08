from argparse import ArgumentParser
from collections import defaultdict

import common_module
import numpy
import os
import json

def main(root_dir, iterations, page_list):
    pages = common_module.get_pages(page_list)
    result = defaultdict(list)
    for page in pages:
        for i in range(0, iterations - 1):
            path_i = os.path.join(root_dir, str(i), page)
            path_i_1 = os.path.join(root_dir, str(i+1), page)
            if not os.path.exists(path_i) or not os.path.exists(path_i_1):
                continue
            urls_i, sizes_i = get_urls(os.path.join(path_i, 'network_' + page))
            urls_i_1, sizes_i_1 = get_urls(os.path.join(path_i_1, 'network_' + page))
            diff, size = check_diff(urls_i, urls_i_1, sizes_i, sizes_i_1)
            result[page].append((len(diff), size))

    for p in result:
        output_line = p
        cnt_list = []
        for d in result[p]:
            output_line += ' ' + str(d[0]) + ' ' + str(d[1])
            cnt_list.append(d[0])
        median = numpy.median(cnt_list)
        output_line += ' ' + str(int(median))
        print output_line

def check_diff(set_1, set_2, sizes_1, sizes_2):
    result = []
    sizes = 0
    for u in set_1:
        if u not in set_2:
            result.append(u)
            try:
                sizes += sizes_1[u]
            except:
                pass
    return result, sizes

def get_urls(network_filename):
    urls = set()
    sizes = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event['method'] == 'Network.responseReceived':
                request_id = network_event['params']['requestId']
                url = network_event['params']['response']['url']
                if not url.startswith('data'):
                    urls.add(url)
                    try:
                        sizes[url] = int(network_event['params']['response']['headers']['content-length'])
                    except:
                        pass
    return urls, sizes

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('iterations', type=int)
    parser.add_argument('page_list')
    args = parser.parse_args()
    main(args.root_dir, args.iterations, args.page_list)
