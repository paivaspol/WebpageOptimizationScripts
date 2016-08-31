from argparse import ArgumentParser
from collections import defaultdict

import os
import simplejson as json
import subprocess
import numpy

def main(root_dir, page_to_time_mapping, ip_to_rtt_mapping_file):
    # Find all IP addresses and RTT mapping.
    all_ip_rtt_mappings = find_ip_rtt_mapping_all_times(ip_to_rtt_mapping_file)
    all_ips = set(all_ip_rtt_mappings.keys())

    page_to_median_rtts = dict()
    for page, time in page_to_time_mapping.iteritems():
        # if 'abcnews.go.com' not in page:
        #     continue
        page_pcap = os.path.join(root_dir, time, 'pcap', page + '.pcap')

        median_rtts_for_page = dict()
        
        # Find the IP addresses and RTTs associated to this page.
        rtt_objects_for_page = find_ip_rtt_mapping_from_one_file(page_pcap)
        all_ip_rtt_mappings_for_page = get_ip_rtt_mapping_with_min_samples(all_ip_rtt_mappings[page], args.min_samples)
        all_ips_for_page_median_load = set(rtt_objects_for_page.keys())
        all_ips_for_page_all_loads = set(all_ip_rtt_mappings_for_page.keys())
        # print all_ips_for_page_median_load
        # print all_ips_for_page_all_loads
        common_ip_addresses = all_ips_for_page_all_loads & all_ips_for_page_median_load
        ip_rtt_mappings_for_page_with_enough_samples = get_mapping_for_median_load(common_ip_addresses, all_ip_rtt_mappings_for_page)
        page_stat = find_min_max_median_for_page(ip_rtt_mappings_for_page_with_enough_samples)
        print '{0} {1} {2} {3}'.format(page, page_stat[0], page_stat[1], page_stat[2])

def find_min_max_median_for_page(ip_rtt_mappings):
    all_values = []
    for samples in ip_rtt_mappings.values():
        all_values.extend(samples)
    min_value = min(all_values)
    max_value = max(all_values)
    median_value = numpy.median(all_values)
    return min_value, median_value, max_value

def get_mapping_for_median_load(common_ip_addresses, all_ip_rtt_mappings_for_page):
    return { key: value for key, value in all_ip_rtt_mappings_for_page.iteritems() if key in common_ip_addresses }

def get_ip_rtt_mapping_with_min_samples(ip_to_rtt_map, min_samples):
    return { key: value for key, value in ip_to_rtt_map.iteritems() if min_samples == 0 or len(value) >= min_samples }

def find_ip_rtt_mapping_from_one_file(pcap_path):
    command = 'python -u pcap.py {0}'.format(pcap_path)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    rtts_obj = None
    stdout, stderr = process.communicate()
    process.wait()

    for line in stdout.split(os.linesep):
        if line != '':
            rtts_obj = json.loads(line)
    return rtts_obj

def find_ip_rtt_mapping_all_times(ip_rtt_mappings_file):
    with open(ip_rtt_mappings_file, 'rb') as input_file:
        return json.load(input_file)

def get_page_to_time_mapping(page_to_time_mapping_filename):
    with open(page_to_time_mapping_filename, 'rb') as input_file:
        splitted_lines = [ x.strip().split() for x in input_file ]
        return { page: time for page, time in splitted_lines }

def get_times(times):
    with open(times, 'rb') as input_file:
        return [ x.strip() for x in input_file ]

def extract_page_from_filename(pcap_filename):
    return pcap_filename[:len(pcap_filename) - len('.pcap')]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_to_time_mapping')
    parser.add_argument('ip_to_rtt_mapping_file')
    parser.add_argument('--min-samples', default=0, type=int)
    args = parser.parse_args()
    page_to_time_mapping = get_page_to_time_mapping(args.page_to_time_mapping)
    main(args.root_dir, page_to_time_mapping, args.ip_to_rtt_mapping_file)
