from argparse import ArgumentParser
from collections import defaultdict

import os
import numpy

def main(directories):
    page_stats = defaultdict(list) # mapping from page --> list of parsing times
    for directory in directories:
        pages = os.listdir(directory)
        for page in pages:
            parsing_time_filename = os.path.join(directory, page, 'html_parsing_runtime.txt')
            if os.path.exists(parsing_time_filename):
                with open(parsing_time_filename, 'rb') as input_file:
                    runtime = float(input_file.readline().strip().split()[0])
                    page_stats[page].append(runtime)

    for page in page_stats:
        parsing_times = page_stats[page]
        median = numpy.median(parsing_times)
        average = numpy.average(parsing_times)
        stdev = numpy.std(parsing_times)
        variance = numpy.var(parsing_times)
        print '{0} {1} {2} {3} {4}'.format(page, median, average, stdev, variance)
        if args.print_raw_parsing_times:
            print '\t{0}'.format(parsing_times)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('directories', nargs='*')
    parser.add_argument('--print-raw-parsing-times', default=False, action='store_true')
    args = parser.parse_args()
    main(args.directories)
