from argparse import ArgumentParser

import os
import subprocess

def find_low_utilizations_in_directory(root_dir, thresholds):
    '''
    Finds the low utilizations in a directory.
    '''
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            continue
        print 'Path: ' + path
        utilization_filename = os.path.join(path, 'bandwidth.txt')
        start_end_interval_filename = os.path.join(path, 'start_end_time_ignoring_bytes.txt')
        if os.path.exists(utilization_filename) and os.path.exists(start_end_interval_filename):
            command = 'python find_low_utilization_time.py {0} {1} {2} --output-dir {3}'.format(utilization_filename, start_end_interval_filename, construct_thresholds_str(thresholds), path)
            subprocess.call(command, shell=True)

def construct_thresholds_str(thresholds):
    threshold_str = ''
    for threshold in thresholds:
        threshold_str += str(threshold) + ' '
    return threshold_str.strip()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('thresholds', type=float, nargs='*')
    args = parser.parse_args()
    find_low_utilizations_in_directory(args.root_dir, args.thresholds)
