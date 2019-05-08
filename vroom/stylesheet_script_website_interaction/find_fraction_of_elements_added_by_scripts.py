from argparse import ArgumentParser
from collections import defaultdict

import os

TOTAL_ELEMENTS = 'total_elements'
ADDED_ELEMENTS = 'added_elements'

def get_stats(root_dir):
    histogram = defaultdict(lambda: 0)
    for path, dirs, filenames in os.walk(root_dir):
        for filename in filenames:
            page_filename = os.path.join(path, filename)
            page_stat = get_stat_for_page(page_filename)
            merge_histograms(histogram, page_stat)
    print_histogram(histogram)

#################################################################
# Output Related
def print_histogram(histogram):
    added_elements = histogram[ADDED_ELEMENTS]
    total_elements = histogram[TOTAL_ELEMENTS]
    fraction_added = 1.0 * added_elements / total_elements
    print 'total_elements ' + str(total_elements)
    print 'added_elements ' + str(added_elements)
    print 'fraction_added ' + str(fraction_added)
    tag_results = []
    for tag, count in histogram.iteritems():
        if tag != TOTAL_ELEMENTS and tag != ADDED_ELEMENTS:
            fraction_of_added = 1.0 * count / added_elements
            tag_results.append((tag, count, fraction_of_added))
    tag_results.sort(key=lambda x : x[2], reverse=True)
    for tag_result in tag_results:
        print '{0} {1} {2}'.format(tag_result[0], tag_result[1], tag_result[2])

################################################################
# Helper functions
def merge_histograms(base, additional_data):
    for tag, count in additional_data.iteritems():
        base[tag] += count
            
def get_stat_for_page(filename):
    '''
    Returns a dictionary mapping from the tag to the count.
    '''
    result = dict()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    get_stats(args.root_dir)
