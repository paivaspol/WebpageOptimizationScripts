from argparse import ArgumentParser
from multiprocessing import Pool, freeze_support

import itertools
import sys
import commands
import json
import os
import datetime

NUM_PROCESSES = 8

def CalculateSpeedIndex(root_dir, page, output_dir):
    print 'Computing: ' + page
    trace_filename = os.path.join(root_dir, page, 'tracing_' + page)
    if not os.path.exists(trace_filename):
        return

    data = []
    temp_file = '{0}.tmp'.format(page)
    with open(trace_filename) as f:
        for line in f:
            data.append(line.strip())

    fout = open(temp_file,'w')

    fout.write('[')
    just_started = True
    cur_line = ''
    for a_data in data:
        cur_line += a_data
        try:
            event = json.loads(cur_line)
        except Exception:
            continue

        cur_line = '' # Reset cur_line

        if "value" in event['params']:
            for i in range(len(event['params']['value'])):
                a_value = event['params']['value'][i]
                if just_started:
                    just_started = False
                    fout.write(json.dumps( a_value ))
                else:
                    fout.write(',\n'+json.dumps( a_value ))
    fout.write(']')
    fout.close()
    
    e = commands.getstatusoutput('speedline ' + temp_file)
    os.remove(temp_file)
    if e[0] == 0:
        output_results(output_dir, page, e[1])
    else:
        output_results(output_dir, page, e)

def output_results(output_dir, page, result):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        output_file.write(result)

def calculate_speed_index_helper(args):
    return CalculateSpeedIndex(*args)

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = os.listdir(root_dir)
    worker_pool = Pool(NUM_PROCESSES)
    try:
        worker_pool.map(calculate_speed_index_helper, itertools.izip(itertools.repeat(root_dir), \
                                                      pages, itertools.repeat(output_dir)))
    except:
        pass

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    freeze_support()
    main(args.root_dir, args.output_dir)
