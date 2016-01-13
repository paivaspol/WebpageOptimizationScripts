from argparse import ArgumentParser

import os
import subprocess

def rename_start_end_time_files(root_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        for filename in filenames:
            if filename.startswith('start_end_time') or filename.startswith('network'):
                new_filename = filename.replace('www.', '')
                full_file_path = os.path.join(path, filename)
                full_new_file_path = os.path.join(path, new_filename)
                command = 'mv {0} {1}'.format(full_file_path, full_new_file_path)
                print command
                subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    rename_start_end_time_files(args.root_dir)
