from argparse import ArgumentParser

import common_module
import dpkt
import os
import math
import numpy

INTERVAL_SIZE = 100 # ms
BANDWIDTH = 4 # mbps

def main(root_dir, end_time_offset_dict):
    pages = os.listdir(root_dir)
    if args.page_list is not None:
        pages = filter_page_not_on_page_list(pages, args.page_list)
    for page in pages:
        page_directory = os.path.join(root_dir, page)
        start_end_time_filename = os.path.join(page_directory, 'start_end_time_' + page)
        pcap_file = os.path.join(page_directory, 'output.pcap')
        if not os.path.exists(start_end_time_filename) or \
            not os.path.exists(pcap_file):
            continue
        start_time, end_time = get_start_end_time(start_end_time_filename)
        custom_end_time = end_time
        if page in end_time_offset_dict:
            custom_end_time = min(start_time + end_time_offset_dict[page], end_time)
        bytes_during_custom_end, bytes_per_interval = populate_bytes_per_interval(pcap_file, start_time, custom_end_time, end_time)
        # print len(utilizations)
        # print utilizations
        total_bytes_before_custom_end = sum(bytes_during_custom_end)
        total_bytes = sum(bytes_per_interval)
        try:
            fraction = 1.0 * total_bytes_before_custom_end / total_bytes
            print '{0} {1} {2} {3}'.format(page, total_bytes_before_custom_end, total_bytes, fraction)
        except ZeroDivisionError:
            pass

def filter_page_not_on_page_list(pages, page_list):
    pages_set = set(pages)
    with open(page_list, 'rb') as input_file:
        wanted_pages = set()
        for raw_line in input_file:
            escaped_page = common_module.escape_page(raw_line.strip().split()[1])
            wanted_pages.add(escaped_page)
        return pages_set & wanted_pages

def populate_bytes_per_interval(pcap_file, start_time, custom_end_time, end_time):
    bytes_during_custom_end = generate_buckets(start_time, custom_end_time)
    buckets = generate_buckets(start_time, end_time)
    with open(pcap_file, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        try:
            for ts, buf in pcap_objects:
                ts = ts * 1000
                if not start_time <= ts < end_time:
                    # The current timestamp is not in the page interval.
                    continue
                elif ts >= end_time:
                    break
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    # Only use IP packets 
                    continue
                ip = eth.data
                try:
                    udp = ip.data
                    # if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                    #     # We only care about HTTP or HTTPS
                    #     continue
                    if int(ip.p) == int(dpkt.ip.IP_PROTO_UDP) or udp.sport == 1194:
                        index = int(1.0 * (ts - start_time) / INTERVAL_SIZE)
                        buckets[index] += ip.len
                        if start_time <= ts < custom_end_time:
                            bytes_during_custom_end[index] += ip.len
                except Exception as e:
                    pass
        except dpkt.NeedData as e1:
            pass
    return bytes_during_custom_end, buckets

def compute_utilization(bytes_received_list, start_interval, end_interval):
    '''
    Returns a list of utilization
    '''
    result = []
    for i in range(0, len(bytes_received_list)):
        bytes_received = bytes_received_list[i]
        interval_size = INTERVAL_SIZE
        if i == len(bytes_received_list) - 1:
            interval_size = (end_interval - start_interval) % INTERVAL_SIZE
        try:
            utilization = common_module.compute_utilization(bytes_received, \
                                                            bandwidth=BANDWIDTH, \
                                                            interval=interval_size)
            result.append(utilization)
        except Exception:
            # DivisionError
            pass
    return result

def get_start_end_time(start_end_time_filename):
    with open(start_end_time_filename, 'rb') as input_file:
        splitted_line = input_file.readline().strip().split()
        return (int(splitted_line[1]), int(splitted_line[2]))

def generate_buckets(start_interval, end_interval):
    '''
    Generates a list with size of the expected buckets
    '''
    buckets = []
    num_slots = int(math.ceil(1.0 * (end_interval - start_interval) / INTERVAL_SIZE))
    for i in range(0, num_slots):
        buckets.append(0)
    return buckets

def populate_end_time_offset_dict(custom_end_time_filename, end_time_offset_dict):
    with open(custom_end_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            end_time_offset_dict[line[0]] = float(line[1]) * 1000.0 # convert to ms

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_load_root_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--custom-end-time', default=None)
    args = parser.parse_args()
    end_time_offset_dict = dict()
    if args.custom_end_time is not None:
        populate_end_time_offset_dict(args.custom_end_time, end_time_offset_dict)
    main(args.page_load_root_dir, end_time_offset_dict)
