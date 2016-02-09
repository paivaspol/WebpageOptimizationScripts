from argparse import ArgumentParser

import common_module

FILENAME_PREFIX = '192.168.2.1_page_load_experiments_'
HTML_SUFFIX = '.html'

def parse_network_throughput_bound_file(network_throughput_bound_page_load_time_filename):
    result = dict()
    with open(network_throughput_bound_page_load_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            page_name = extract_page_name_from_filename(line[0])
            result[page_name] = float(line[1])
    print len(result)
    print result.keys()
    return result

def extract_page_name_from_filename(filename):
    extracted_page_name = filename[len(FILENAME_PREFIX):len(filename) - len(HTML_SUFFIX)]
    return common_module.escape_page(extracted_page_name)

def parse_cpu_bound_file(cpu_bound_page_load_time_filename, page_map):
    result = dict()
    with open(cpu_bound_page_load_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            page = line[0]
            if page.endswith('_'):
                page = page[:len(page) - 1]
            if page in page_map:
                page = page_map[page]
            result[page.replace('.', '_')] = float(line[1])
    print len(result)
    print result.keys()
    return result
                
def parse_page_map(page_map_filename):
    result = dict()
    with open(page_map_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) > 1:
                result[common_module.escape_page(line[1])] = common_module.escape_page(line[0])
    return result

def parse_original_page_load_file(original_page_load_filename):
    result = dict()
    with open(original_page_load_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[common_module.escape_page(line[0]).replace('.', '_')] = float(line[1])
    print len(result)
    print result.keys()
    return result

def find_max(network_bound_plts, cpu_bound_plts, original_plts):
    dict_with_more_pages = network_bound_plts
    if len(cpu_bound_plts) > len(dict_with_more_pages):
        dict_with_more_pages = cpu_bound_plts
    if len(original_plts) > len(dict_with_more_pages):
        dict_with_more_pages = original_plts
    for page in dict_with_more_pages:
        if page in cpu_bound_plts and page in network_bound_plts and page in original_plts:
            cpu_plt = cpu_bound_plts[page]
            network_plt = network_bound_plts[page]
            print '{0} {1} {2} {3} {4}'.format(page, cpu_plt, network_plt, max(cpu_plt, network_plt), original_plts[page])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('cpu_bound_page_load_time_filename')
    parser.add_argument('network_throughput_bound_page_load_time_filename')
    parser.add_argument('original_page_load_filename')
    parser.add_argument('page_map_filename')
    args = parser.parse_args()
    page_map = parse_page_map(args.page_map_filename)
    network_bound_plts = parse_network_throughput_bound_file(args.network_throughput_bound_page_load_time_filename)
    cpu_bound_plts = parse_cpu_bound_file(args.cpu_bound_page_load_time_filename, page_map)
    original_plts = parse_original_page_load_file(args.original_page_load_filename)
    find_max(network_bound_plts, cpu_bound_plts, original_plts)
