from argparse import ArgumentParser

import sys
import commands
import json
import os
import datetime

def CalculateSpeedIndex(trace_file):
    data = []
    temp_file = 'speedindex.tmp'
    with open(trace_file) as f:
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
        # print event

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
        return e[1]
    else:
        return e

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        trace_filename = os.path.join(root_dir, page, 'tracing_' + page)
        if not os.path.exists(trace_filename):
            print trace_filename
            continue
        speedindex = CalculateSpeedIndex(trace_filename)
        if isinstance(speedindex, basestring) and speedindex.startswith('First Visual'):
            print page
            print speedindex
            print ''

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
