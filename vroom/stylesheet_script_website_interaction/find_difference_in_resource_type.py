from argparse import ArgumentParser

def parse_stat_file(first_stat_filename, second_stat_filename, resource_type):
    first_pages_histogram = populate_data_structure(first_stat_filename)
    second_pages_histogram = populate_data_structure(second_stat_filename)
    for page in first_pages_histogram:
        first_page_histogram = first_pages_histogram[page]
        second_page_histogram = second_pages_histogram[page]
        if len(first_page_histogram) == 0:
            continue
        elif resource_type in first_page_histogram:
            first_page_value = int(first_page_histogram[resource_type][0])
            second_page_value = 0
            if resource_type in second_page_histogram:
                second_page_value = int(second_page_histogram[resource_type][0])
            difference = first_page_value - second_page_value
            print '{0} {1}'.format(page, difference)

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
    parser.add_argument('first_stat_filename')
    parser.add_argument('second_stat_filename')
    parser.add_argument('resource_type')
    args = parser.parse_args()
    parse_stat_file(args.first_stat_filename, args.second_stat_filename, args.resource_type)
