from argparse import ArgumentParser

import common_module
import subprocess
import os

def main(root_dir, use_spdyproxy):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        trace_filename = os.path.join(path, 'output.pcap')
        page_load_interval_filename = os.path.join(path, 'start_end_time_{0}'.format(url))
        command = 'python bandwidth_calculator.py {0} {1} {2}'.format(trace_filename, page_load_interval_filename, path)
        if use_spdyproxy:
            command += ' --use-spdyproxy'
        subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--use-spdyproxy', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.use_spdyproxy)

