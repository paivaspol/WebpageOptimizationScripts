from argparse import ArgumentParser

import os
import numpy

def find_request_sizes(root_dir):
    request_dictionary = dict()
    cumulative_time = 0
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        interval_request_filename = os.path.join(path, '100ms_interval_num_request.txt')
        with open(interval_request_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                num_request = int(line[2])
                time = float(line[1]) - float(line[0])
                if num_request not in request_dictionary:
                    request_dictionary[num_request] = 0
                request_dictionary[num_request] += float(line[1]) - float(line[0])
                cumulative_time += time
    return request_dictionary, cumulative_time

def write_to_file(results, cumulative_time, output_filename):
    sorted_results_dict = sorted(results.items(), key=lambda x: x[0])
    with open(output_filename, 'wb') as output_file:
        cumulative_sum = 0.0
        for result in sorted_results_dict:
            cumulative_sum += result[1] / cumulative_time
            output_file.write(str(result[0]) + ' ' + str(results[1]) + ' ' + str(cumulative_sum) + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    request_dictionary, cumulative_time = find_request_sizes(args.root_dir)
    output_filename = os.path.join(args.output_dir, 'fraction_of_time.txt')
    write_to_file(request_dictionary, cumulative_time, output_filename)
