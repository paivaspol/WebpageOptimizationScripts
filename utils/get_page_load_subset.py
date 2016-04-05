from argparse import ArgumentParser

import common_module

def pick_page_load_time(page_load_time_filename, page_set):
    with open(page_load_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if common_module.escape_page(line[0]) in page_set:
                print raw_line.strip()

def get_page_set(page_list_filename):
    result = set()
    with open(page_list_filename, 'rb') as input_file:
        for raw_line in input_file:
            line  = raw_line.strip().split()
            url = common_module.escape_page(line[len(line) - 1])
            result.add(url)
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_load_time_filename')
    parser.add_argument('page_list_filename')
    args = parser.parse_args()
    page_set = get_page_set(args.page_list_filename)
    pick_page_load_time(args.page_load_time_filename, page_set)
