from argparse import ArgumentParser

import dpkt
import math
import numpy
import os

import common_module

SUBINTERVAL_SIZE = 100
BANDWIDTH = 6 # mbps

def find_utilization_during_interval(root_dir):
    result = []
    page_utilization_breakdown = dict()
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        pcap_full_path = os.path.join(path, 'output.pcap')
        interval_border_filename = os.path.join(path, 'interval_border_evenly_breakdown.txt')
        if not (os.path.exists(pcap_full_path) and os.path.exists(interval_border_filename)):
            continue
        intervals = get_interval_time(interval_border_filename)
        page_load_start_time = intervals[0][0][0]
        page_load_end_time = intervals[len(intervals) - 1][0][1]
        current_interval_index = 0
        current_interval = intervals[current_interval_index][0]
        with open(pcap_full_path, 'rb') as pcap_file:
            pcap_objects = dpkt.pcap.Reader(pcap_file)
            bytes_received = generate_buckets(intervals)
            try:
                for ts, buf in pcap_objects:
                    ts = ts * 1000
                    if not page_load_start_time <= ts <= page_load_end_time:
                        # The current timestamp is not in the page interval.
                        # print 'page load start: ' + str(page_load_start_time) + ' page load end: ' + str(page_load_end_time) + ' ts: ' + str(ts)
                        # print 'here (0)'
                        continue
                    elif ts > page_load_end_time:
                        # print 'here (1)'
                        # Out of the page load process range
                        break
                    elif ts > current_interval[1]:
                        # print 'here (2)'
                        # Out of the current interval range. Update the interval index and get the next interval.
                        current_interval_index += 1
                        if current_interval_index >= len(intervals):
                            break
                        current_interval = intervals[current_interval_index][0]

                    eth = dpkt.ethernet.Ethernet(buf)
                    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                        # Only use IP packets 
                        continue
                    ip = eth.data
                    try:
                        tcp = ip.data
                        if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                            # We only care about HTTP or HTTPS
                            continue
                        bytes_received[current_interval_index][int((ts - current_interval[0]) / SUBINTERVAL_SIZE)] += ip.len
                    except Exception as e:
                        pass
            except dpkt.NeedData as e1:
                pass
            utilizations = compute_utilization(bytes_received, intervals)
            print 'utilizations len: ' + str(utilizations)
            add_utilizations(result, utilizations)
            page_utilization_breakdown[url] = utilizations
    return result, page_utilization_breakdown

def get_interval_time(interval_filename):
    interval_dict = dict()
    with open(interval_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        for i in range(0, len(line) - 1):
            start_ts = float(line[i])
            end_ts = float(line[i + 1])
            interval_dict[(start_ts, end_ts)] = i
    sorted_interval_dict = sorted(interval_dict.iteritems(), key=lambda x: x[0][0])
    return sorted_interval_dict

def generate_buckets(intervals):
    '''
    Generates a list with size of the expected buckets
    '''
    buckets = []
    num_slots = len(intervals)
    # First, generate the buckets for each interval.
    for i in range(0, num_slots):
        buckets.append([])
    # Second, generate the buckets for each time breakdown.
    for i in range(0, num_slots):
        current_interval = intervals[i][0]
        num_buckets_breakdown = int(math.ceil(1.0 * (current_interval[1] - current_interval[0]) / SUBINTERVAL_SIZE))
        for j in range(0, num_buckets_breakdown):
            buckets[i].append(0)
    return buckets

def add_utilizations(result, utilizations):
    while len(result) < len(utilizations):
        result.append([])

    for i in range(0, len(utilizations)):
        result[i].append(utilizations[i])

def compute_utilization(bytes_received_list, intervals):
    '''
    Returns a list of utilization broken down to intervals
    '''
    result = []
    for i in range(0, len(bytes_received_list)):
        bytes_received_per_interval = bytes_received_list[i]
        current_interval = intervals[i][0]
        utilizations_during_interval = []
        for j in range(0, len(bytes_received_per_interval)):
            bytes_received = bytes_received_per_interval[j]
            if j == len(bytes_received_list) - 1:
                interval_size = (current_interval[1] - current_interval[0]) % SUBINTERVAL_SIZE
            else:
                interval_size = SUBINTERVAL_SIZE
            utilization = common_module.compute_utilization(bytes_received, bandwidth=BANDWIDTH, interval=SUBINTERVAL_SIZE)
            # print 'bytes received: ' + str(bytes_received) + ' utilization: ' + str(utilization)
            utilizations_during_interval.append(utilization)
        average_utilization = numpy.mean(utilizations_during_interval)
        result.append(average_utilization)
    return result

def print_results(results, output_dir):
    print 'len result: ' + str(len(results))
    for i in range(0, len(results)):
        utilizations_all_pages = results[i]
        utilizations_all_pages.sort()
        output_filename = os.path.join(output_dir, str(i))
        with open(output_filename, 'wb') as output_file:
            for utilization in utilizations_all_pages:
                output_file.write(str(utilization) + '\n')

def output_samples(page_utilization_breakdown, output_dir):
    output_filename = os.path.join(output_dir, 'each_page_utilization_breakdown.txt')
    with open(output_filename, 'wb') as output_file:
        for url in page_utilization_breakdown:
            utilization_breakdown = page_utilization_breakdown[url]
            if len(utilization_breakdown) > 2:
                # We choose the second lowest, median, and the second highest utilization.
                utilization_breakdown.sort()
                lower_sample = utilization_breakdown[1]
                upper_sample = utilization_breakdown[len(utilization_breakdown) - 2]
                median_sample = numpy.median(utilization_breakdown)
                line = '{0} {1} {2} {3}\n'.format(url, median_sample, lower_sample, upper_sample)
                output_file.write(line)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    results, page_utilization_breakdown = find_utilization_during_interval(args.root_dir)
    print_results(results, args.output_dir)
    output_samples(page_utilization_breakdown, args.output_dir)
