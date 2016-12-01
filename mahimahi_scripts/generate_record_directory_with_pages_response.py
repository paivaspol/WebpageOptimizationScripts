from argparse import ArgumentParser

import os
import subprocess


def main(root_dir, page_to_timestamp_filename, output_dir):
    page_to_timestamp_mapping = get_page_to_timestamp_mapping(page_to_timestamp_filename)
    for page, timestamp in page_to_timestamp_mapping:
        page_directory = os.path.join(root_dir, timestamp, page)
        index_files = find_index_files(page_directory, page, output_dir)
        if len(index_files) > 1:
            print '{0} {1}'.format(page, len(index_files))

def find_index_files(page_directory, page, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        print page
        page_directory = os.path.join(root_dir, page)
        if not os.path.exists(page_directory):
            continue
        generate_record_directories_with_responses(page_directory, page, output_dir)

def generate_record_directories_with_responses(page_directory, page, output_dir):
    recorded_files = os.listdir(page_directory)
    result = []
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))
    for recorded_file in recorded_files:
        full_path_to_recorded_file = os.path.join(page_directory, recorded_file)
        output_filename = os.path.join(output_dir, page, recorded_file)
        top_cmd = './generate_pages_with_scheduling_logic/protototext {0} {1}'.format(full_path_to_recorded_file, output_filename)
        subprocess.call([top_cmd], stdout=subprocess.PIPE, shell=True)

def get_page_to_timestamp_mapping(page_to_timestamp_filename):
    with open(page_to_timestamp_filename, 'rb') as input_file:
        return [ line.strip().split() for line in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_to_timestamp_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.page_to_timestamp_filename, args.output_dir)
