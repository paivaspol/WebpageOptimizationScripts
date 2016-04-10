from argparse import ArgumentParser

def get_page_load_time(filename):
    result = dict()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = float(line[1])
    return result

def find_difference(first_dict, second_dict):
    result = []
    for key, load_time in first_dict.iteritems():
        if key in second_dict:
            diff = load_time - second_dict[key]
            result.append((key, diff))
    return result

def print_result(diff_result):
    sorted_diff_result = sorted(diff_result, key=lambda x: x[1])
    for result in sorted_diff_result:
        print '{0} {1}'.format(result[0], result[1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    args = parser.parse_args()
    first_dict = get_page_load_time(args.first_file)
    second_dict = get_page_load_time(args.second_file)
    differences = find_difference(first_dict, second_dict)
    print_result(differences)
