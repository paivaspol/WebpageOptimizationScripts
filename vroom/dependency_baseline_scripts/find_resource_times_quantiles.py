from argparse import ArgumentParser

import os
import numpy

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        times_filename = os.path.join(root_dir, page)
        times = []
        with open(times_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                times.append(float(line[1]))
        min_time = min(times)
        tenth = numpy.percentile(times, 10)
        twentyfifth = numpy.percentile(times, 25)
        median = numpy.percentile(times, 50)
        seventyfifth = numpy.percentile(times, 75)
        nintieth = numpy.percentile(times, 90)
        max_time = max(times)
        print '{0} {1} {2} {3} {4} {5}'.format(page, min_time, tenth, twentyfifth, median, seventyfifth, nintieth, max_time)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
