from argparse import ArgumentParser

def main(page_to_run_index_dict, times):
    for page, run_index in page_to_run_index_dict.iteritems():
        print '{0} {1}'.format(page, times[run_index])

def get_page_to_run_index_dict(page_to_run_index_filename):
    result = dict()
    with open(page_to_run_index_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_to_run_index_mapping')
    parser.add_argument('times', nargs='+')
    args = parser.parse_args()
    page_to_run_index_dict = get_page_to_run_index_dict(args.page_to_run_index_mapping)
    main(page_to_run_index_dict, args.times)
