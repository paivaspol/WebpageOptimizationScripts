from argparse import ArgumentParser

import common_module
import json
import os

def write_to_file(output_dir, page, result):
    with open(os.path.join(output_dir, page), 'wb') as output_file:
        for url, discovery, net_wait_time, _ in result:
            line = url + '\t' + str(discovery) + '\t' + str(net_wait_time)
            output_file.write(line + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    for p in os.listdir(args.root_dir):
        timing_filename = os.path.join(args.root_dir, p, 'timings.txt')
        result = common_module.get_preloaded_timings(timing_filename)
        write_to_file(args.output_dir, p, result)
