from argparse import ArgumentParser

import common_module
import os

def find_low_utilizations(utilization_intervals, interval_size, start_end_interval, thresholds):
    total_time = (start_end_interval[1][1] - start_end_interval[1][0])
    results = []
    for threshold in thresholds:
        low_utilization_time = 0.0
        for i in range(0, len(utilization_intervals)):
            if i < len(utilization_intervals) - 1:
                if utilization_intervals[i][1] <= threshold:
                    low_utilization_time += interval_size
            else:
                # Case for last interval.
                left_over_time = total_time % interval_size
                if utilization_intervals[i][1] <= threshold:
                    low_utilization_time += left_over_time
        # print 'total time: {0} low_utilization_time: {1}'.format(total_time, low_utilization_time)
        results.append(low_utilization_time)
    return results, total_time

def output_low_utilizations(total_time, results, thresholds, output_dir):
    full_path = os.path.join(output_dir, 'low_utilization_times')
    with open(full_path, 'wb') as output_file:
        header = '# total_time '
        for threshold in thresholds:
            header += str(threshold) + ' '
        header.strip()
        output_file.write(header + '\n')
        line = str(total_time)
        for result in results:
            line += ' ' + str(result) 
        output_file.write(line + '\n')

def parse_utilizations(utilization_filename):
    '''
    Parses the utilizations
    '''
    result = []
    first_interval = None
    second_interval = None
    with open(utilization_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.append((int(line[0]), float(line[1])))
            if first_interval is None:
                first_interval = int(line[0])
            elif second_interval is None:
                second_interval = int(line[0])
    return result, (second_interval - first_interval)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('utilization_filename')
    parser.add_argument('start_end_time_filename')
    parser.add_argument('thresholds', type=float, nargs='*')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    start_end_interval = common_module.parse_page_start_end_time(args.start_end_time_filename)
    utilization_intervals, interval_size = parse_utilizations(args.utilization_filename)
    results, total_time = find_low_utilizations(utilization_intervals, interval_size, start_end_interval, args.thresholds)
    output_low_utilizations(total_time, results, args.thresholds, args.output_dir)
