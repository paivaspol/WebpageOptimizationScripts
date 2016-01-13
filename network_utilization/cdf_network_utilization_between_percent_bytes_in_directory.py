from argparse import ArgumentParser

import os
import subprocess

def main(root_dir, lower_percentage, upper_percentage, use_spdyproxy):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        command = 'python cdf_network_utilization_between_percent_bytes.py {0} {1} {2}'.format(path, lower_percentage, upper_percentage)
        if use_spdyproxy:
            command += ' --use-spdyproxy'
        # print command
        subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('lower_percentage')
    parser.add_argument('upper_percentage')
    parser.add_argument('--use-spdyproxy', action='store_true', default=False)
    args = parser.parse_args()
    main(args.root_dir, args.lower_percentage, args.upper_percentage, args.use_spdyproxy)

