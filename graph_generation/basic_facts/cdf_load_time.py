from argparse import ArgumentParser

import os

def get_load_time(root_dir):
    results = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = extract_url(path)
        full_path = os.path.join(path, 'start_end_time_' + url)
        if os.path.exists(full_path):
            with open(full_path, 'rb') as input_file:
                line = input_file.readline().strip().split()
                load_time = int(line[2]) - int(line[1])
                if load_time > 0:
                    results.append(load_time)
    results.sort()
    for result in results:
        print result

def extract_url(path):
    delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            delim_index = i
    return path[delim_index + 1:]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    get_load_time(args.root_dir)

