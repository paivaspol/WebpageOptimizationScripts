from argparse import ArgumentParser
from urlparse import urlparse

import os

def main(first_dir, second_dir):
    pages = os.listdir(first_dir)
    for page in pages:
        try:
            print page
            first_dir_resource_sizes = get_resource_sizes(first_dir, page)
            second_dir_resource_sizes = get_resource_sizes(second_dir, page)
            #print first_dir_resource_sizes
            #print second_dir_resource_sizes
            for resource_url in first_dir_resource_sizes:
                parsed_url = urlparse(resource_url)
                for second_resource_url in second_dir_resource_sizes:
                    parsed_second_resource_url = urlparse(second_resource_url)
                    if parsed_url.path == parsed_second_resource_url.path and \
                        parsed_url.query == parsed_second_resource_url.query and \
                        parsed_url.params == parsed_second_resource_url.params and \
                        parsed_url.fragment == parsed_second_resource_url.fragment:
                        print '\t' + second_resource_url + ' ' + str(first_dir_resource_sizes[resource_url]) + ' ' + str(second_dir_resource_sizes[second_resource_url])
                        break
        except Exception as e:
            pass

def get_resource_sizes(directory, page):
    filename = os.path.join(directory, page, 'resource_size.txt')
    with open(filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file if len(line.strip().split()) == 2 ]
        return { key: value for key, value in temp if not key.startswith('data:') }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_dir')
    parser.add_argument('second_dir')
    args = parser.parse_args()
    main(args.first_dir, args.second_dir)
