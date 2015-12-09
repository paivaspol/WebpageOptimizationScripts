from argparse import ArgumentParser

import os

def generate_graph_data(root_dir):
    intervals = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        interval_border_filename = 'interval_border.txt'
        full_path = os.path.join(path, interval_border_filename)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as input_file:
                line = input_file.readline().strip().split()
                intervals.append(line)
    return get_interval_size(intervals)

def get_interval_size(intervals):
    result = []
    for i in range(0, (len(intervals[0]) - 1) + 2):
        result.append([])
    for interval in intervals:
        if len(interval) > 0:
            for i in range(0, len(interval) - 1):
                result[i].append(float(interval[i + 1]) - float(interval[i]))
            result[len(result) - 2].append(float(interval[2]) - float(interval[0]))
            result[len(result) - 1].append(float(interval[len(interval) - 1]) - float(interval[len(interval) - 3]))
    for i in range(0, len(result)):
        result[i].sort()
    return result

def output_to_file(interval_sizes, output_dir):
    for i in range(0, len(interval_sizes)):
        if i == len(interval_sizes) - 2:
            full_path = os.path.join(output_dir, 'interval_0_1.txt')
        elif i == len(interval_sizes) - 1:
            full_path = os.path.join(output_dir, 'interval_3_4.txt')
        else:
            full_path = os.path.join(output_dir, 'interval_' + str(i) + '.txt')
        interval_size = interval_sizes[i]
        with open(full_path, 'wb') as output_file:
            for result in interval_size:
                output_file.write('{0}\n'.format(result))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    interval_sizes = generate_graph_data(args.root_dir)
    output_to_file(interval_sizes, args.output_dir)
