from argparse import ArgumentParser

import simplejson as json
import subprocess
import os
import numpy

def main(pcap_path):
    command = 'python -u pcap.py {0}'.format(pcap_path)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rtts_obj = None
    while True:
        line = process.stdout.readline()
        if line != '':
            rtts_obj = json.loads(line.strip())
            # print line
        else:
            break
    if rtts_obj is not None:
        result = find_median(rtts_obj)
        for page, median_rtt in result.iteritems():
            print '{0} {1}'.format(page, median_rtt)

def find_median(rtts_obj):
    result = dict()
    for page, rtts in rtts_obj.iteritems():
        if args.min_samples == 0 or len(rtts) >= args.min_samples:
            result[page] = numpy.median(rtts)
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_file')
    parser.add_argument('--min-samples', default=0, type=int)
    args = parser.parse_args()
    main(args.pcap_file)
