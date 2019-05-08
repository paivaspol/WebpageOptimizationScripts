from argparse import ArgumentParser

import os
import subprocess

def main(root_dir, page_to_timestamp, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = os.listdir(root_dir)
    for page in pages:
        timestamp = page_to_timestamp[page]
        timestamp_output_dir = os.path.join(output_dir, timestamp)
        if not os.path.exists(timestamp_output_dir):
            os.mkdir(timestamp_output_dir)
        src = os.path.join(root_dir, page)
        command = 'mv {0} {1}'.format(src, timestamp_output_dir)
        subprocess.call(command, shell=True)

def get_page_to_timestamp(page_to_timestamp):
    with open(page_to_timestamp, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: value for key, value in temp }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_to_timestamp')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    page_to_timestamp = get_page_to_timestamp(args.page_to_timestamp)
    main(args.root_dir, page_to_timestamp, args.output_dir)
