from argparse import ArgumentParser

import common_module

def main(page_list_filename, page_to_time_mappings):
    pages = get_pages(page_list_filename)
    page_to_timestamp_mappings_dict = get_page_to_timestamp_mappings(page_to_time_mappings)
    for page in pages:
        if page in page_to_timestamp_mappings_dict:
            print '{0} {1}'.format(page, page_to_timestamp_mappings_dict[page])

def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        return [ common_module.escape_page(line.strip()) for line in input_file ]

def get_page_to_timestamp_mappings(page_to_time_mappings):
    result = dict()
    for mapping_filename in page_to_time_mappings:
        with open(mapping_filename, 'rb') as input_file:
            temp = [ line.strip().split() for line in input_file ]
            result.update({ key: value for key, value in temp })
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_list_file')
    parser.add_argument('page_to_time_mappings', nargs='+')
    args = parser.parse_args()
    main(args.page_list_file, args.page_to_time_mappings)
