from argparse import ArgumentParser

import os
import subprocess

def main(root_dir, times, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for time in times:
        time_directory = os.path.join(root_dir, time)
        output_time_directory = os.path.join(output_dir, time)
        if not os.path.exists(output_time_directory):
            os.mkdir(output_dir)

        pages = os.listdir(time_directory)
        for page in pages:
            # This is already the source directory.
            # Use this directory and use the modify_page.py
            # To include the scheduler.
            page_directory = os.path.join(time_directory, page)
            output_directory = os.path.join(output_time_directory, page)
            generate_command = 'python ./generate_pages_with_scheduling_logic/modify_page.py {0} {1}'
            subprocess.call(generate_command.format(page_directory, output_directory), shell=True)

def get_times(time_filename):
    with open(time_filename, 'rb') as input_file:
        return [ line.strip().split()[0] for line in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('times')
    parser.add_argument('output_dir')
    args = parsre.parse_args()
    times = get_times(args.times)
    main(args.root_dir, times, args.output_dir)
