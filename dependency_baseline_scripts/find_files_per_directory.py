from argparse import ArgumentParser
from collections import defaultdict

import os

def main(root_dir, num_iterations):
    result_dict = defaultdict(list)
    for i in range(0, num_iterations):
        pages = os.listdir(os.path.join(root_dir, str(i)))
        for page in pages:
            base_files = { 'chromium_log.txt', 'cpu_running_chrome.txt', 'network_' + page, 'start_end_time_' + page }
            path = os.path.join(root_dir, str(i), page)
            files = { name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name)) }
            missing_files = base_files - files
            result_dict[page].append((i, missing_files))

    page_missing_files = []
    for page in result_dict:
        did_miss_file = False
        print 'page: ' + page
        missing_files_list = result_dict[page]
        for iteration, missing_files in missing_files_list:
            if len(missing_files) > 0:
                did_miss_file = True
                print '\tIteration {0}: Missing {1} files. Files missing: {2}'.format(iteration, len(missing_files), missing_files)
        if did_miss_file:
            page_missing_files.append(page)
    print 'Total Pages: {0}'.format(len(result_dict))
    print '# Page Missing Files: {0}. Pages: {1}'.format(len(page_missing_files), page_missing_files)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('num_iterations', type=int)
    args = parser.parse_args()
    main(args.root_dir, args.num_iterations)
