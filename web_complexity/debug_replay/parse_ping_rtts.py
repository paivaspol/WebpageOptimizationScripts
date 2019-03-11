from argparse import ArgumentParser
from collections import defaultdict

import numpy

def Main():
    cur_ip = ''
    ip_to_rtts = defaultdict(list)
    with open(args.ping_results, 'r') as input_file:
        for l in input_file:
            l = l.strip()
            if l.startswith('PING'):
                splitted = l.split()
                cur_ip = splitted[1]
            elif l.startswith('64 bytes'):
                time_index = l.index('time')
                time = l[time_index:]
                time_ms = ParseTime(time)
                ip_to_rtts[cur_ip].append(time_ms)

    # Find median
    for ip, rtts in ip_to_rtts.items():
        print('{0} {1}'.format(ip, float(numpy.median(rtts)) + args.base_delay))


def ParseTime(time):
    '''
    Returns the time in milliseconds.
    '''
    time = time.split('=')
    retval = ''
    for c in time[1]:
        if not c.isdigit():
            break
        retval += c
    return int(retval)
    

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('ping_results')
    parser.add_argument('--base-delay', default=0, type=float)
    args = parser.parse_args()
    Main()
