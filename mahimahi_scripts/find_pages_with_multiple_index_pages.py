from argparse import ArgumentParser

import os
import subprocess

def main(root_dir, page_to_timestamp_filename):
    page_to_timestamp_mapping = get_page_to_timestamp_mapping(page_to_timestamp_filename)
    for page, timestamp in page_to_timestamp_mapping:
        page_directory = os.path.join(root_dir, timestamp, page)
        index_files = find_index_files(page_directory)
        if len(index_files) > 1:
            print '{0} {1}'.format(page, len(index_files))

def find_index_files(page_directory):
    recorded_files = os.listdir(page_directory)
    result = []
    for recorded_file in recorded_files:
        top_cmd = './generate_pages_with_scheduling_logic/protototext {0} {1}'.format(recorded_file, 'temp.out')
        proc_top = subprocess.Popen([top_cmd], stdout=subprocess.PIPE, shell=True)
        (out_top, err_top) = proc_top.communicate()
        out_top = out_top.strip("\n")
        if ( "type=htmlindex" in out_top ): # this is the top-level HTML
            top_level_html = out_top.split("na--me=")[1]
            result.append(filename)

        rm_cmd = 'rm temp.out'
        subprocess.call(rm_cmd, shell=True)
    return result

def get_page_to_timestamp_mapping(page_to_timestamp_filename):
    with open(page_to_timestamp_filename, 'rb') as input_file:
        return [ line.strip().split() for line in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_to_timestamp_filename')
    args = parser.parse_args()
    main(args.root_dir, args.page_to_timestamp_filename)
