from argparse import ArgumentParser

import os

def main(first_dir, second_dir):
    first_dir_parsing_times = get_parsing_times(first_dir)
    second_dir_parsing_times = get_parsing_times(second_dir)
    results = []
    for page in first_dir_parsing_times:
        if page in second_dir_parsing_times:
            diff = first_dir_parsing_times[page] - second_dir_parsing_times[page]
            results.append((page, diff))
    sorted_results = sorted(results, key=lambda x: x[1])
    for result in sorted_results:
        print '{0} {1}'.format(result[0], result[1])

def get_parsing_times(directory):
    result = dict()
    pages = os.listdir(directory)
    for page in pages:
        parsing_time_filename = os.path.join(directory, page, 'html_parsing_runtime.txt')
        if not os.path.exists(parsing_time_filename):
            continue
        with open(parsing_time_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                result[page] = float(line[0])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_dir')
    parser.add_argument('second_dir')
    args = parser.parse_args()
    main(args.first_dir, args.second_dir)
