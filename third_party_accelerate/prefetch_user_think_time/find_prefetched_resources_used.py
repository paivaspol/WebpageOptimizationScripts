'''
Another key important question to answer is the number of resources actually
used from prefetching.
'''
from argparse import ArgumentParser
from collections import defaultdict

import common_module
import numpy
import os
import random

PERCENTILES = [ 5, 25, 50, 75, 95 ]

def Main():
    histogram, page_resources = \
            GetHistogramAndPageResourceMapping(args.root_dir)
    pages = SelectPages(page_resources.keys(), args.num_pages)
    with open('page_resources_count', 'w') as output_file:
        for p in pages:
            output_file.write('{0} {1}\n'.format(p, len(page_resources[p])))

    sorted_histogram = sorted(histogram.items(), \
                            key=lambda x: (x[1], x[0]), \
                            reverse=True)
    prefetching = set()
    for resource_url, _ in sorted_histogram:
        prefetching.add(resource_url)

        fractions = []
        for p in pages:
            page_intersection = prefetching & page_resources[p]
            fractions.append(
                    1.0 * len(page_intersection) / len(page_resources[p]))

        output = '{0}'.format(len(prefetching))
        for percentile in PERCENTILES:
            output += ' ' + \
                    str(numpy.percentile(fractions, percentile))
        print(output)


def GetHistogramAndPageResourceMapping(crawl_dir):
    histogram = defaultdict(int)
    page_resources = {}
    for p in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        urls = common_module.GetURLs(network_filename)
        for u in urls:
            histogram[u] += 1
        page_resources[p] = urls
    return histogram, page_resources


def SelectPages(pages, num_pages):
    '''
    Returns a list of selected pages.

    The default implementation sorts the pages alphabetically and pick the first
    n pages from the list.
    '''
    random.seed(42)
    pages_list = list(pages)
    return random.sample(pages_list, num_pages)
    

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir', \
            help='The root directory that  contains the crawl data')
    parser.add_argument('--num-pages', \
                        type=int, \
                        help='The number of pages to consider', \
                        default=50)
    args = parser.parse_args()
    Main()
