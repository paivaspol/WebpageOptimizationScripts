from argparse import ArgumentParser

def get_page_load_time(filename):
    result = dict()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = float(line[1])
    return result

def do_operation(first_dict, second_dict, mode):
    result_list = []
    # vice.com_en_us pi.eecs.umich.edu_bulk_pages_vice.com_en_us
    for key, load_time in first_dict.iteritems():
        for second_dict_key, second_dict_load_time in second_dict.iteritems():
            if key in second_dict_key:
                result = None
                if mode == 'diff':
                    result = load_time - second_dict[second_dict_key]
                elif mode == 'max':
                    result = max(load_time, second_dict[second_dict_key])

                if result is not None:
                    result_list.append((key, result))
                break
    return result_list

def print_result(diff_result):
    sorted_diff_result = sorted(diff_result, key=lambda x: x[1])
    for result in sorted_diff_result:
        print '{0} {1}'.format(result[0], result[1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    parser.add_argument('mode')
    args = parser.parse_args()
    first_dict = get_page_load_time(args.first_file)
    second_dict = get_page_load_time(args.second_file)
    result_list = do_operation(first_dict, second_dict, args.mode)
    print_result(result_list)
