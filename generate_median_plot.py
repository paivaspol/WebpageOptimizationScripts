from argparse import ArgumentParser

import numpy

import common_module

LOAD_TIME_THRESHOLD = 250

def output_median(pages_to_utilization, longest_load_len, output_filename):
    time_index = 0
    with open(output_filename, 'wb') as output_file:
        while time_index < longest_load_len:
            current_utilizations = []
            for page in pages_to_utilization:
                utilizations = pages_to_utilization[page]
                if time_index < len(utilizations):
                    current_utilizations.append(utilizations[time_index])
            median = numpy.median(current_utilizations)
            output_file.write(str(time_index * 100) + ' ' + str(median) + '\n')
            time_index += 1

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
    output_median(page_to_utilization_map, longest_load_len, args.output_filename)
