from argparse import ArgumentParser
from collections import defaultdict

import itertools
import os
import numpy

def Main():
    urls_requests = GetURLs(args.root_dir)
    pages = urls_requests.keys()
    intersection_size = defaultdict(list)
    all_num_requests = defaultdict(list)
    for i in xrange(2, len(pages) + 1):
        all_combinations = itertools.combinations(pages, i)
        for c_i, c in enumerate(all_combinations):
            intersection, num_requests = FindIntersection(c, urls_requests)
            intersection_size[i].append(len(intersection))
            all_num_requests[i].append(num_requests)
            if i == len(pages) and args.output_intersected is not None:
                with open(args.output_intersected, 'w') as output_file:
                    for url in intersection:
                        output_file.write(url + '\n')

    for i, vals in intersection_size.iteritems():
        print '{0} {1} {2} {3} {4} {5} {6}'.format(i, min(vals), numpy.percentile(vals, 25), numpy.median(vals), numpy.percentile(vals, 75), max(vals), numpy.median(all_num_requests[i]))

def FindIntersection(pages, urls_requests):
    intersection = None
    num_requests = []
    for p in pages:
        if intersection is None:
            intersection = set(urls_requests[p])
            num_requests.append(len(urls_requests[p]))
            continue
        intersection &= urls_requests[p]
        num_requests.append(len(urls_requests[p]))
    return intersection, numpy.mean(num_requests)


def GetURLs(root_dir):
    result = {}
    pages = os.listdir(root_dir)
    for p in pages:
        urls = set()
        with open(os.path.join(root_dir, p), 'r') as input_file:
            for l in input_file:
                urls.add(l.strip())
        result[p] = urls
    return result


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--output-intersected', default=None)
    args = parser.parse_args()
    Main()
