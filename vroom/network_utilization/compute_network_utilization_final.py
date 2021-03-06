from argparse import ArgumentParser

import common_module
import dpkt
import os
import math
import numpy
import subprocess

INTERVAL_SIZE = 100 # ms
BANDWIDTH = 12 # mbps

def main(root_dir, start_time_dict, end_time_offset_dict):
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
        total_time = end_time - start_time
        if page in end_time_offset_dict:
            end_time = min(start_time + end_time_offset_dict[page], end_time)
        if page in start_time_dict:
            start_time = start_time + start_time_dict[page]
        dependency_time = end_time - start_time
        bytes_per_interval = populate_bytes_per_interval(pcap_file, start_time, end_time)
        utilizations = compute_utilization(bytes_per_interval, start_time, end_time)
        # print len(utilizations)
        # print utilizations
        if len(utilizations) > 0:
            average_utilization = numpy.average(utilizations)
            # print 'TotalTime: {0} {1}'.format(page, total_time)
            # print 'DependencyTime: {0} {1}'.format(page, dependency_time)
            # print '{0} {1}'.format(page, utilizations)
            # print '{0} {1}'.format(page, len(utilizations))
            print '{0} {1}'.format(page, average_utilization)
            # print ''

        if args.output_timeseries:
            if not os.path.exists(args.output_timeseries):
                os.mkdir(args.output_timeseries)
            output_timeseries(args.output_timeseries, page, utilizations)

def output_timeseries(output_dir, page, utilizations):
    page_output_dir = os.path.join(output_dir, page)
    if not os.path.exists(page_output_dir):
        os.mkdir(page_output_dir)
    page_output = os.path.join(page_output_dir, 'data.txt')
    with open(page_output, 'wb') as output_file:
        for i, utilization in enumerate(utilizations):
            output_file.write('{0} {1}\n'.format(i, utilization))
    # Copy the script for the timeseries.
    subprocess.call('cp plot_timeseries.R {0}'.format(page_output_dir).split())

def filter_page_not_on_page_list(pages, page_list):
    pages_set = set(pages)
    with open(page_list, 'rb') as input_file:
        wanted_pages = set()
        for raw_line in input_file:
            escaped_page = common_module.escape_page(raw_line.strip().split()[1])
            wanted_pages.add(escaped_page)
        return pages_set & wanted_pages

def populate_bytes_per_interval(pcap_file, start_time, end_time):
    buckets = generate_buckets(start_time, end_time)
    with open(pcap_file, 'rb') as pcap_file:
        try:
            pcap_objects = dpkt.pcap.Reader(pcap_file)
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
                except Exception as e:
                    pass
        except dpkt.NeedData as e1:
            pass
    return buckets

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
            # utilization = min(1.0, common_module.compute_utilization(bytes_received, \
            #                                                 bandwidth=BANDWIDTH, \
            #                                                 interval=interval_size))
            utilization = common_module.compute_utilization(bytes_received, \
                                                            bandwidth=BANDWIDTH, \
                                                            interval=interval_size)
            result.append(utilization)
        except Exception:
            # DivisionError
            pass
    # result.append(min(1.0, common_module.compute_utilization(sum(bytes_received_list), bandwidth=BANDWIDTH, interval=(end_interval - start_interval))))
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

def populate_start_time_dict(start_time_filename, start_time_dict):
    with open(start_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            start_time_dict[line[0]] = float(line[1]) * 1000

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_load_root_dir')
    parser.add_argument('--page-list', default=None)
    parser.add_argument('--custom-start-time', default=None)
    parser.add_argument('--custom-end-time', default=None)
    parser.add_argument('--output-timeseries', default=None)
    args = parser.parse_args()

    start_time_dict = dict()
    if args.custom_start_time:
        populate_start_time_dict(args.custom_start_time, start_time_dict)

    end_time_offset_dict = dict()
    if args.custom_end_time is not None:
        populate_end_time_offset_dict(args.custom_end_time, end_time_offset_dict)
    main(args.page_load_root_dir, start_time_dict, end_time_offset_dict)
