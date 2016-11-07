from argparse import ArgumentParser

import os

def main(root_dir):
    pages = os.listdir(root_dir)
    results = []
    for page in pages:
        results.extend(get_processing_times(os.path.join(root_dir, page), page))
    results.sort(key=lambda x: x[1])
    for result in results:
        print result[0] + ' ' + str(result[1])

def get_processing_times(server_side_log_filename, page):
    with open(server_side_log_filename, 'rb') as input_file:
        result = []
        for raw_line in input_file:
            line = raw_line.strip().split()
            method = line[1]
            resource = line[2]
            if method == 'GET' and resource == '/':
                process_time = 1.0 * int(line[4]) / 1000
                result.append((page, process_time))
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
