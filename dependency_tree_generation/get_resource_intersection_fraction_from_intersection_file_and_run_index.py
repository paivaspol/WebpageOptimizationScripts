from argparse import ArgumentParser

def main(intersection_fraction_filename, page_to_run_index):
    with open(intersection_fraction_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            # Line Format: soccerway.com 0 41 53 0.77358490566
            url = line[0]
            run_index = line[1]
            total_resources = int(line[3])
            if url in page_to_run_index:
                target_run_index = page_to_run_index[url]
                if run_index == target_run_index:
                    if total_resources > 0:
                        print raw_line.strip()

def get_page_to_run_index(page_to_run_index_filename):
    with open(page_to_run_index_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: value for key, value in temp }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('intersection_fraction_filename')
    parser.add_argument('page_to_run_index_filename')
    args = parser.parse_args()
    page_to_run_index = get_page_to_run_index(args.page_to_run_index_filename)
    main(args.intersection_fraction_filename, page_to_run_index)
