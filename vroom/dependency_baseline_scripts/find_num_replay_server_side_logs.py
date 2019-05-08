from argparse import ArgumentParser 

import common_module
import os

def main(root_dir, page_to_run_index_filename):
    pages = os.listdir(root_dir)
    page_to_run_index = get_page_to_run_index(page_to_run_index_filename)
    for page in pages:
        if page in page_to_run_index:
            replay_count = parse_log(os.path.join(root_dir, page), page, page_to_run_index[page])
            print '{0} {1}'.format(page, replay_count)

def parse_log(log_filename, page, index):
    found_first_request = False
    count = 0
    with open(log_filename, 'rb') as input_file:
        for raw_line in input_file:
            if raw_line.startswith('['):
                continue

            line = raw_line.strip().split(' ')

            # Construct full path of the request.
            port = line[len(line) - 1].split(':')[1]
            scheme = 'https://' if port == '443' else 'http://'
            host = line[len(line) - 2]
            path = line[2]
            url = scheme + host + path
            escaped_url = common_module.escape_page(url)
            if escaped_url == page:
                # We found a new replay. Create a new entry for this replay.
                count += 1
                found_first_request = True
            
            if not found_first_request:
                # Don't do anything when the current timings is None
                continue
    return count

def get_page_to_run_index(page_to_run_index):
    with open(page_to_run_index, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: int(value) for key, value in temp }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('log_root_dir')
    parser.add_argument('page_to_run_index')
    args = parser.parse_args()
    main(args.log_root_dir, args.page_to_run_index)
