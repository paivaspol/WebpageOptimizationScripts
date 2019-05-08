from argparse import ArgumentParser

import sys
import json

input_filename = sys.argv[1]

with open(input_filename, 'rb') as input_file:
    for raw_line in input_file:
        page_timings = json.loads(raw_line.strip())
        page = page_timings['page']
        total_time = int(page_timings['total_time'])
        idle_time = int(page_timings['idle'])
        fraction = 1.0 * idle_time / total_time
        print '{0} {1} {2} {3}'.format(page, idle_time, total_time, fraction)

