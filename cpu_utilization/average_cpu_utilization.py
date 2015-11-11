from argparse import ArgumentParser

import numpy

LIMIT = 10000 / 100

def find_average_utilization(pages_to_utilization, output_filename):
    results = []
    for page, utilizations in pages_to_utilization.iteritems():
        print 'Page: ' + page
        average = numpy.mean(utilizations[:LIMIT])
        if not numpy.isnan(average):
            results.append(average)
    results.sort()
    
    # Output the averages
    with open(output_filename, 'wb') as output_file:
        for result in results:
            output_file.write(str(result) + '\n')

def parse_page_to_utilization_map(pages_to_utilization, load_time_threshold=None):
    retval = dict()
    longest_load_len = -1
    with open(pages_to_utilization, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.rstrip().split()
            utilizations = []
            for i in range(1, len(line)):
                utilizations.append(float(line[i]))
            if load_time_threshold is None or len(utilizations) < load_time_threshold:
                retval[line[0]] = utilizations
                longest_load_len = max(longest_load_len, len(utilizations))
                print str(len(utilizations))
    return retval, longest_load_len

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_to_utilization')
    parser.add_argument('output_filename')
    args = parser.parse_args()
    page_to_utilization_map, longest_load_len = parse_page_to_utilization_map(args.pages_to_utilization)
    find_average_utilization(page_to_utilization_map, args.output_filename)


