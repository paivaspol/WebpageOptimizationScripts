from argparse import ArgumentParser
from collections import defaultdict

import os
import numpy

def Main():
    stats = defaultdict(list)
    for i, d in enumerate(os.listdir(args.root_dir)):
        pages_stats = GetPageStats(os.path.join(args.root_dir, d))
        for url in pages_stats:
            stats[url].append(pages_stats[url])

    for url in stats:
        max_val = max([ x[1] for x in stats[url] ])
        min_val = min([ x[1] for x in stats[url] ])
        median_val = numpy.median([ x[1] for x in stats[url] ])
        variance = 1.0 * (max_val - min_val) / median_val
        print('{0} {1} {2} {3} {4}'.format(url, min_val, median_val, max_val, variance))


def GetPageStats(stat_filename):
    result = {}
    with open(stat_filename, 'r') as input_file:
        for l in input_file:
            l = l.strip().split()
            result[l[0]] = (int(l[1]), int(l[2]))
    return result


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
