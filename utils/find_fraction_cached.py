from argparse import ArgumentParser

import common_module

def parse_file(filename):
    result = dict()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            page = line[0]
            result[page] = int(line[1])
    return result

def generate_map(pages_filename):
    result = dict()
    with open(pages_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) > 1:
                result[common_module.escape_page(line[1])] = common_module.escape_page(line[0])
    print len(result)
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_filename')
    parser.add_argument('cached_page_sizes')
    parser.add_argument('reference_page_sizes')
    parser.add_argument('--ignore-pages', default=None)
    args = parser.parse_args()
    pages_to_ignore = common_module.parse_pages_to_ignore(args.ignore_pages)
    pages_map = generate_map(args.pages_filename)
    cached_page_sizes = parse_file(args.cached_page_sizes)
    reference_page_sizes = parse_file(args.reference_page_sizes)
    for page in cached_page_sizes:
        if page in cached_page_sizes and page in reference_page_sizes \
            and page not in pages_to_ignore:
            cached_page_size = cached_page_sizes[page]
            if page in pages_map:
                page = pages_map[page]
            reference_page_size = reference_page_sizes[page]
            fraction = 1.0 * cached_page_size / reference_page_size
            print '{0} {1}'.format(page, fraction)
    print pages_to_ignore
