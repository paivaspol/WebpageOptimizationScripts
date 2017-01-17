from argparse import ArgumentParser

import common_module
import subprocess
import os

def find_walltime_sorted(root_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        filename = os.path.join(path, 'network_' + url)
        command = 'python check_network_trace_timestamp_sorted.py {0}'.format(filename)
        subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    find_walltime_sorted(args.root_dir)

