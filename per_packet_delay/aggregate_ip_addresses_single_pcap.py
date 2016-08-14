from argparse import ArgumentParser
from collections import defaultdict

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
        print len(set(rtts_obj.keys()))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_file')
    parser.add_argument('--min-samples', default=0, type=int)
    args = parser.parse_args()
    main(args.pcap_file)
