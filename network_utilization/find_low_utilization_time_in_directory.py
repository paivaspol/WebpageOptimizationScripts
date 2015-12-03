from argparse import ArgumentParser

import os
import subprocess

def find_low_utilizations_in_directory(root_dir):
    '''
    Finds the low utilizations in a directory.
    '''
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            continue
        print 'Path: ' + path
        pcap_filename = os.path.join(path, 'output.pcap')
        start_end_interval_filename = os.path.join(path, 'start_end_time_ignoring_bytes.txt')
        if os.path.exists(pcap_filename) and os.path.exists(start_end_interval_filename):
            start_end_interval = parse_start_end_interval(start_end_interval_filename)
            command = 'python find_low_utilization_time.py {0} {1} {2}'.format(pcap_filename, start_end_interval[0], start_end_interval[1])
            subprocess.call(command, shell=True)

def parse_start_end_interval(start_end_interval_filename):
    with open(start_end_interval_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return (line[0], line[1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    find_low_utilizations_in_directory(args.root_dir)
