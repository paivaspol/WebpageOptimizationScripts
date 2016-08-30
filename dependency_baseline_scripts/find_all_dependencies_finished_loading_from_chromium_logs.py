from argparse import ArgumentParser
from datetime import datetime

import common_module
import os
import simplejson as json

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        dependencies = common_module.get_dependencies(dependency_filename)
        chromium_log_filename = os.path.join(root_dir, page, 'chromium_log.txt')
        start_time, latest_timestamp = parse_chromium_log(chromium_log_filename, dependencies)
        discovery_time = (latest_timestamp - start_time) / 1000.0
        print '{0} {1}'.format(page, discovery_time)

def parse_chromium_log(chromium_log_filename, dependency_set):
    start_time = None
    latest_timestamp = -1
    with open(chromium_log_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split(' ')
            timestamp_str = '2016-' + line[0] + ' ' + line[1]
            if start_time is None and 'Starting Asynchronous' in raw_line:
                datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                epoch = datetime.utcfromtimestamp(0)
                millis_since_epoch = (datetime_obj - epoch).total_seconds() * 1000.0
                start_time = millis_since_epoch
            elif 'INFO:resource_dispatcher_host_impl.cc(1182)' in raw_line:
                # The request is finished downloading.
                url = line[len(line) - 4]
                datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                epoch = datetime.utcfromtimestamp(0)
                millis_since_epoch = (datetime_obj - epoch).total_seconds() * 1000.0
                timestamp = millis_since_epoch
                if url in dependency_set:
                    dependency_set.remove(url)
                    latest_timestamp = max(latest_timestamp, timestamp)
    return start_time, latest_timestamp

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
