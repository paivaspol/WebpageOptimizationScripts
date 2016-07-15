from argparse import ArgumentParser

import os

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        chromium_log_filename = os.path.join(root_dir, page, 'chromium_log.txt')
        start_end_time_filename = os.path.join(root_dir, page, 'start_end_time_' + page)
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not os.path.exists(chromium_log_filename):
            continue
        # if not (os.path.exists(chromium_log_filename) and \
        #         os.path.exists(start_end_time_filename) and \
        #         os.path.exists(dependency_filename)):
        #     continue
        # dependency_set = populate_dependencies(dependency_filename)
        # start_time, _ = get_start_end_time(start_end_time_filename)
        parse_chromium_log(chromium_log_filename, start_end_time_filename, dependency_filename)
        break

def populate_dependencies(dependency_filename):
    dependency_set = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            dependency_set.add(line[2])
    return dependency_set

def get_start_end_time(start_end_time_filename):
    with open(start_end_time_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return int(line[1]), int(line[2])

def parse_chromium_log(chromium_log_filename, start_time, dependency_set):
    with open(chromium_log_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            timestamp = '2016-' + line[0] + ' ' + line[1]
            if 'Submitting Dependency Request' in raw_line:
                url = line[len(line) - 1]
                timestamp = int(line[len(line) - 2])
                print '{0} {1}'.format(url, timestamp)

            # 07-12 10:50:01.674 10179 10237 I chromium: [INFO:spdy_stream.cc(128)] Started a SPDY stream.
            # try:
            #     date_object = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            #     date_since_epoch = int(date_object.strftime('%s')) * 1000
            #     if int(date_since_epoch) > int(ms_since_epoch):
            #         break
            # except Exception as e:
            #     pass

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
