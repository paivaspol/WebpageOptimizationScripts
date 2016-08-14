from argparse import ArgumentParser
from collections import defaultdict

import simplejson as json
import subprocess
import os
import numpy

def main(root_dir, output_dir, times):
    unique_ips = set()
    for record_time in times:
        pcap_dir = os.path.join(root_dir, record_time, 'pcap')
        files = os.listdir(pcap_dir)
        for pcap_filename in files:
            pcap_path = os.path.join(pcap_dir, pcap_filename)
            command = 'python -u pcap.py {0}'.format(pcap_path)
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while True:
                line = process.stdout.readline()
                if line != '':
                    rtts_obj = json.loads(line.strip())
                    # print rtts_obj
                    for ip in rtts_obj:
                        unique_ips.add(ip)
                else:
                    break
    print len(unique_ips)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('times', nargs='+')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir, args.times)
