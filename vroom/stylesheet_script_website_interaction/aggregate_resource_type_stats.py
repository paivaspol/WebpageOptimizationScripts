from argparse import ArgumentParser

def parse_stat_file(stat_filename, resource_type):
    pages_histogram = populate_data_structure(stat_filename)
    for page in pages_histogram:
        histogram = pages_histogram[page]
        if len(histogram) == 0:
            continue
        elif resource_type in histogram:
            values = histogram[resource_type]
            print '{0} {1} {2} {3}'.format(page, values[0], values[1], values[2])
        elif resource_type not in histogram:
            values = histogram.values()[0]
            print '{0} {1} {2} {3}'.format(page, 0, values[1], 0.0)

def populate_data_structure(stat_filename):
    page_histograms = dict()
    with open(stat_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) == 1:
                page = line[0]
                page_histograms[page] = dict()
            elif raw_line.startswith('\t'):
                if len(line) == 4:
                    page_histograms[page][line[0].replace('.', '')] = (line[1], line[2], line[3])
                else:
                    page_histograms[page]['other'] = (line[2], line[3], line[4])
    return page_histograms

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('stat_filename')
    parser.add_argument('resource_type')
    args = parser.parse_args()
    parse_stat_file(args.stat_filename, args.resource_type)
