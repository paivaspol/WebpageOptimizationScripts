from argparse import ArgumentParser

import os
import json

def main(timing_filename):
    with open(timing_filename, 'rb') as input_file:
        for l in input_file:
            timing = json.loads(l.strip())
            load_time = timing['total_time']
            idle_time = timing['idle']
            p = timing['page']
            print p + ' ' + str((1.0 * (load_time - idle_time) / 1000000.0)) + ' ' + str(idle_time)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('timing_filename')
    args = parser.parse_args()
    main(args.timing_filename)
