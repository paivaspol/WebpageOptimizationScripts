from argparse import ArgumentParser

import os
import subprocess

WWW_PREFIX = 'www.'

def rename_directories_and_files(root_dir):
    dirs = os.listdir(root_dir)
    for path in dirs:
        last_delim_index = find_last_delim_index(path)
        directory_name = path[last_delim_index + 1:]
        if directory_name.startswith('_'):
            fix_directory_and_file(directory_name, root_dir, path, '_')
        elif directory_name.startswith(WWW_PREFIX):
            fix_directory_and_file(directory_name, root_dir, path, WWW_PREFIX)

def fix_directory_and_file(directory_name, root_dir, path, prefix):
    # Fix the directory names
    fixed_url = directory_name[len(prefix):]
    current_url = directory_name
    current_dir_path = os.path.join(root_dir, path)
    new_dir_path = os.path.join(root_dir, fixed_url)
    mv_command = 'mv {0} {1}'.format(current_dir_path, new_dir_path)
    print mv_command
    subprocess.call(mv_command, shell=True)

    # Fix the file names inside the directory.
    current_filename = os.path.join(new_dir_path, 'start_end_time_' + current_url)
    new_filename = os.path.join(new_dir_path, 'start_end_time_' + fixed_url)
    mv_file_command = 'mv {0} {1}'.format(current_filename, new_filename)
    print mv_file_command
    subprocess.call(mv_file_command, shell=True)
        
def find_last_delim_index(path):
    index = -1
    for i in range(0, len(path)):
        if path[i] == os.sep:
            index = i
    return index

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    rename_directories_and_files(args.root_dir)
