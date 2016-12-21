from argparse import ArgumentParser

import os
import subprocess

def main(root_dir):
    for path, _, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            # Ignore directories without files.
            continue
        url = extract_url_from_path(path)
        print 'URL: ' + url
        network_trace_filename = os.path.join(path, 'network_{0}'.format(url))
        bandwidth_filename = os.path.join(path, 'bandwidth.txt')
        command = 'python find_outstanding_requests.py {0} {1} --output-dir {2}'.format(network_trace_filename, bandwidth_filename, path)
        subprocess.call(command, shell=True)

def extract_url_from_path(path):
    '''
    Extracts the url from the given path.
    '''
    index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            index = i
    return path[index + 1:]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
