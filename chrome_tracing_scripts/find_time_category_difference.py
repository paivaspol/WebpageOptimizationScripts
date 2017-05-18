from argparse import ArgumentParser

import os
import json

def get_timings(timing_filename):
    result = dict()
    with open(timing_filename, 'rb') as input_file:
        for l in input_file:
            timing = json.loads(l.strip())
            p = timing['page']
            result[p] = timing
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_timing_filename')
    parser.add_argument('second_timing_filename')
    args = parser.parse_args()
    first_timings = get_timings(args.first_timing_filename)
    second_timings = get_timings(args.second_timing_filename)
    selected_pages = [ 'aljazeera.com', 'nationalgeographic.com', 'redbull.com', 'reddit', 'scout' ]
    for p in first_timings:
        output_line = p
        skip = True
        for sp in selected_pages:
            if sp in p:
                skip = False
        if not skip and p in second_timings:
            first_timing = first_timings[p]
            second_timing = second_timings[p]
            print p
            for cat in first_timing:
                if cat in second_timing:
                    if type(second_timing[cat]) is int:
                        diff = second_timing[cat] - first_timing[cat]
                        if diff > 0:
                            print '\t' + cat + '\t' + str(diff)
