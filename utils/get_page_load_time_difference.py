from argparse import ArgumentParser

import os

def find_load_times(root_dir, other_root_dir):
    result = dict()
    second_result = dict()
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = extract_url_from_path(path)
        full_path = os.path.join(path, 'start_end_time_' + url)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as input_file:
                line = input_file.readline().strip().split()
                load_time = float(line[2]) - float(line[1])
                result[url] = load_time
    for path, dirs, filenames in os.walk(other_root_dir):
        if len(filenames) == 0:
            continue
        url = extract_url_from_path(path)
        full_path = os.path.join(path, 'start_end_time_' + url)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as input_file:
                line = input_file.readline().strip().split()
                load_time = float(line[2]) - float(line[1])
                second_result[url] = load_time
    difference = find_difference(result, second_result)
    sorted_result = sorted(difference.iteritems(), key=lambda x: x[1])
    print_result(sorted_result)

def print_result(results):
    for result in results:
        print str(result[0]) + ' ' + str(result[1])

def find_difference(first_load_time, second_load_time):
    result = dict()
    for key in second_load_time:
        if key in first_load_time:
            result[key] = second_load_time[key] - first_load_time[key]
    return result


def extract_url_from_path(path):
    '''
    Extracts the url from the path.
    '''
    last_delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            last_delim_index = i
    return path[last_delim_index + 1:]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('other_dir')
    args = parser.parse_args()
    find_load_times(args.root_dir, args.other_dir)
