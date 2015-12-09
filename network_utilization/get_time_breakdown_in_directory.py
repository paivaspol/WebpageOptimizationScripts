from argparse import ArgumentParser

import os
import subprocess

import common_module

def find_interval_borders(root_dir, percent_ignoring):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        pcap_full_path = os.path.join(path, 'output.pcap')
        total_bytes_full_path = os.path.join(path, 'bytes_received.txt')
        start_end_time_full_path = os.path.join(path, 'start_end_time_' + url)

        if os.path.exists(pcap_full_path) and \
            os.path.exists(total_bytes_full_path) and \
            os.path.exists(start_end_time_full_path):
            print 'Processing: ' + path
            command = 'python get_time_breakdown.py {0} {1} {2} {3} --output-dir {4}'.format(pcap_full_path, start_end_time_full_path, total_bytes_full_path, percent_ignoring, path)
            subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('percent_ignoring', type=int)
    args = parser.parse_args()
    find_interval_borders(args.root_dir, args.percent_ignoring)
