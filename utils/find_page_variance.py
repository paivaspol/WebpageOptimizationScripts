from argparse import ArgumentParser
from collections import defaultdict

import numpy
import os

def main():
    '''
    Iterates through all the runs of the experiment and compares
    the the PLTs to the median PLT.
    '''
    page_to_plt = defaultdict(list) # Mapping from page URL to [] of PLTs
    for i in range(0, args.iterations):
        if not args.include_first_load and i == '0':
            continue
        iteration_dir = os.path.join(args.root_dir, str(i))
        if not os.path.isdir(iteration_dir):
            # Skip any regular files.
            continue

        pages = os.listdir(iteration_dir)
        for page in pages:
            plt_filename = os.path.join(iteration_dir, page, 'start_end_time_' + page)
            page_to_plt[page].append(get_plt(plt_filename))


    # Show the varinace by displaying the max, min and the median.
    for page, plts in page_to_plt.iteritems():
        median = numpy.median(plts)
        max_plt = max(plts)
        min_plt = min(plts)
        print '{0} {1} {2} {3}'.format(page, min_plt, median, max_plt)

def get_plt(plt_filename):
    '''
    Assumes that the file is in the following format:
        'abcnews.go.com 1491403171532 1491403195912 -1 -1 1491403185537'

    Returns:
        col[2] - col[1]
    '''
    with open(plt_filename, 'r') as input_file:
        line = input_file.read().strip().split(' ')
        return int(line[2]) - int(line[1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('iterations', type=int)
    parser.add_argument('--include-first-load', default=False, action='store_true')
    parser.add_argument('--plot-output')
    args = parser.parse_args()
    main()
