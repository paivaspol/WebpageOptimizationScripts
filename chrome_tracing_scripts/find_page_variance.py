from argparse import ArgumentParser
from collections import defaultdict

import common_module
import os

THRESHOLD = 0.2

def main(root_dirs, iterations, pages):
    max_objs = defaultdict(lambda: -1)
    min_objs = defaultdict(lambda: 500000)
    distribution = defaultdict(list)
    for root_dir in root_dirs:
        for page in pages:
            for i in range(1, iterations):
                request_filename = os.path.join(root_dir, 'extended_waterfall_' + str(i), page, 'ResourceSendRequest.txt')
                if not os.path.exists(request_filename):
                    # print 'Cannot find: ' + request_filename
                    continue
                with open(request_filename, 'rb') as input_file:
                    num_lines = sum([ 1 for raw_line in input_file ])
                    max_objs[page] = max(max_objs[page], num_lines)
                    min_objs[page] = min(min_objs[page], num_lines)
                    distribution[page].append(num_lines)
    
    for page in max_objs:
        if page not in min_objs:
            continue
        max_val = max_objs[page]
        min_val = min_objs[page]
        percent_difference = 1.0 * (max_val - min_val) / min_val
        if not (percent_difference > THRESHOLD and (max_val - min_val > 10)):
            print '{0} {1} {2} {3}'.format(page, min_val, max_val, percent_difference)
            # print '{0} {1}'.format(page, distribution[page])
        else:
            pass
            # print '{0} {1} {2} {3}'.format(page, min_val, max_val, percent_difference)
        # print '{0} {1}'.format(page, distribution[page])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dirs', nargs='+')
    parser.add_argument('iterations', type=int)
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    pages = common_module.get_pages(args.pages_filename)
    main(args.root_dirs, args.iterations, pages)
