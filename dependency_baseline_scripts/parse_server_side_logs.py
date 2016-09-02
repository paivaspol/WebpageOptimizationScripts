from argparse import ArgumentParser 
from datetime import datetime
from dateutil import parser as date_parser

import common_module
import os

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        if 'news.google.com' not in page:
            continue
        print page
        parse_log(os.path.join(root_dir, page))

def parse_log(log_filename):
    with open(log_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split(' ')

            # Get timestamp.
            timestamp = int(line[0]) # microsecond precision

            # Construct full path of the request.
            port = line[len(line) - 1].split(':')[1]
            scheme = 'https://' if port == '443' else 'http://'
            host = line[len(line) - 2]
            path = line[2]
            full_path = scheme + host + path

            # Get the time to serve this request in microseconds.
            time_to_serve = int(line[4])
            completion_time = timestamp + time_to_serve


            print '{0} {1} {2}'.format(timestamp, completion_time, full_path)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
