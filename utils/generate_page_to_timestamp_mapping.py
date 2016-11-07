from argparse import ArgumentParser

def generate_timestamp_mappings(page_to_index_mapping, timestamps):
    with open(page_to_index_mapping, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            page = line[0]
            index = int(line[1])
            print '{0} {1}'.format(page, timestamps[index])

def get_timestamps(timestamp_filename):
    with open(timestamp_filename, 'rb') as input_file:
        return [ x.strip() for x in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_to_index_mapping')
    parser.add_argument('timestamps_list')
    args = parser.parse_args()
    timestamps = get_timestamps(args.timestamps_list)
    generate_timestamp_mappings(args.page_to_index_mapping, timestamps)
