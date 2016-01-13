from argparse import ArgumentParser

import os

def get_fraction_of_time(root_dir, start_interval_index, end_interval_index):
    result = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        intervals_filename = os.path.join(path, 'interval_border.txt')
        if not os.path.exists(intervals_filename):
            continue
        with open(intervals_filename, 'rb') as input_file:
            line = input_file.readline().strip().split()
            total_time = get_time(line, 0, len(line) - 1)
            interval_time = get_time(line, start_interval_index, end_interval_index)
            result.append(1.0 * interval_time / total_time)
    result.sort()
    return result

def get_time(line, start_interval_index, end_interval_index):
    return float(line[end_interval_index]) - float(line[start_interval_index])

def print_result(results):
    for result in results:
        print result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('start_interval_index', type=int)
    parser.add_argument('end_interval_index', type=int)
    args = parser.parse_args()
    result = get_fraction_of_time(args.root_dir, args.start_interval_index, args.end_interval_index)
    print_result(result)
