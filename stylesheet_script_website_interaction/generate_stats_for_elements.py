from argparse import ArgumentParser

import common_module
import os

TOTAL_ELEMENTS = 'total_elements'
ADDED_ELEMENTS = 'added_elements'
FRACTION_ADDED = 'fraction_added'

def get_stats(root_dir, output_dir, elements):
    output_files = get_output_files(elements, output_dir)
    for path, dirs, filenames in os.walk(root_dir):
        for filename in filenames:
            page_filename = os.path.join(path, filename)
            page_stats = common_module.get_stat_for_page(page_filename)
            write_result_to_file(elements, page_stats, output_files)
    close_files(output_files)

def write_result_to_file(elements, page_stats, output_files):
    added_elements = page_stats[ADDED_ELEMENTS]
    total_elements = page_stats[TOTAL_ELEMENTS]
    fraction_added = 1.0 * added_elements / total_elements
    output_files[FRACTION_ADDED].write('{0}\n'.format(fraction_added))
    for element in elements:
        if element in page_stats:
            fraction_added = 1.0 * page_stats[element] / added_elements
            output_files[element].write('{0}\n'.format(fraction_added))
        else:
            output_files[element].write('0\n')

def get_output_files(elements, output_dir):
    output_file_ptrs = dict()
    output_filename = os.path.join(output_dir, FRACTION_ADDED + '.stat')
    output_file_ptrs[FRACTION_ADDED] = open(output_filename, 'wb')
    for element in elements:
        output_filename = os.path.join(output_dir, element + '.stat')
        output_file_ptrs[element] = open(output_filename, 'wb')
    return output_file_ptrs

def close_files(output_files):
    for element, output_file in output_files.iteritems():
        output_file.close()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('elements', nargs='+')
    args = parser.parse_args()
    get_stats(args.root_dir, args.output_dir, args.elements)
