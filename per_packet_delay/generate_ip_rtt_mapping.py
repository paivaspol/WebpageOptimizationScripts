from argparse import ArgumentParser
from collections import defaultdict

import simplejson as json
import subprocess
import os
import numpy

def main(root_dir, output_dir, times):
    page_to_samples = dict()
    for record_time in times:
        pcap_dir = os.path.join(root_dir, record_time, 'pcap')
        files = os.listdir(pcap_dir)
        for pcap_filename in files:
            page_name = extract_page_from_filename(pcap_filename)
            # print page_name
            # if 'news.google' not in page_name:
            #     continue
            # print page_name
            if page_name not in page_to_samples:
                page_to_samples[page_name] = defaultdict(list)

            samples = page_to_samples[page_name]
            pcap_path = os.path.join(pcap_dir, pcap_filename)
            command = 'python -u pcap.py {0}'.format(pcap_path)
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            process.wait()

            for line in stdout.split(os.linesep):
                if line != '':
                    rtts_obj = json.loads(line.strip())
                    for ip in rtts_obj:
                        samples[ip].extend(rtts_obj[ip])

    if args.output_raw_data:
        print json.dumps(page_to_samples)
    elif args.aggregate_samples:
        aggregate_samples(output_dir, page_to_samples)
    else:
        output_rtt_mappings(output_dir, page_to_samples)

def aggregate_samples(output_dir, page_to_samples):
    all_samples = dict()
    for page in page_to_samples:
        samples = page_to_samples[page]
        for ip in samples:
            if ip not in all_samples:
                all_samples[ip] = []
            all_samples[ip].extend(samples[ip])

    for ip in all_samples:
        samples = all_samples[ip]
        if args.min_samples == 0 or len(samples) >= args.min_samples:
            median = numpy.median(samples)
            print '{0} {1}'.format(ip, median) # Also convert to ms

def output_rtt_mappings(output_dir, page_to_samples):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    for page in page_to_samples:
        output_filename = os.path.join(output_dir, page)
        with open(output_filename, 'wb') as output_file:
            samples = page_to_samples[page]
            for ip in samples:
                samples_for_ip = samples[ip]
                median_rtt = numpy.median(samples_for_ip)
                output_file.write('{0} {1}\n'.format(ip, median_rtt))

def extract_page_from_filename(pcap_filename):
    return pcap_filename[:len(pcap_filename) - len('.pcap')]

def get_times(times):
    with open(times, 'rb') as input_file:
        return [ x.strip() for x in input_file ]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('times')
    parser.add_argument('--output-raw-data', default=False, action='store_true')
    parser.add_argument('--aggregate-samples', default=False, action='store_true')
    parser.add_argument('--min-samples', default=0, type=int)
    args = parser.parse_args()
    times = get_times(args.times)
    main(args.root_dir, args.output_dir, times)
