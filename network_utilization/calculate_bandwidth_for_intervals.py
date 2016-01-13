from argparse import ArgumentParser

import dpkt
import math
import numpy
import os

import common_module

SUBINTERVAL_SIZE = 100
BANDWIDTH = 6 # mbps

def find_utilization_during_interval(root_dir, start_interval_index, end_interval_index):
    result = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        pcap_full_path = os.path.join(path, 'output.pcap')
        interval_border_filename = os.path.join(path, 'interval_border.txt')
        if not (os.path.exists(pcap_full_path) and os.path.exists(interval_border_filename)):
            continue
        start_interval, end_interval = get_interval_time(interval_border_filename, start_interval_index, end_interval_index)
        with open(pcap_full_path, 'rb') as pcap_file:
            pcap_objects = dpkt.pcap.Reader(pcap_file)
            bytes_received = generate_buckets(start_interval, end_interval)
            try:
                for ts, buf in pcap_objects:
                    ts = ts * 1000
                    if not start_interval <= ts <= end_interval:
                        # The current timestamp is not in the page interval.
                        continue
                    elif ts > end_interval:
                        break
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
                        bytes_received[int((ts - start_interval) / SUBINTERVAL_SIZE)] += ip.len
                    except Exception as e:
                        pass
            except dpkt.NeedData as e1:
                pass
            utilizations = compute_utilization(bytes_received, start_interval, end_interval)
            average_utilization = numpy.mean(utilizations)
            result.append(average_utilization)
    return result

def get_interval_time(interval_filename, start_interval_index, end_interval_index):
    with open(interval_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return float(line[start_interval_index]), float(line[end_interval_index])

def generate_buckets(start_interval, end_interval):
    '''
    Generates a list with size of the expected buckets
    '''
    buckets = []
    num_slots = int(math.ceil(1.0 * (end_interval - start_interval) / SUBINTERVAL_SIZE))
    for i in range(0, num_slots):
        buckets.append(0)
    return buckets

def compute_utilization(bytes_received_list, start_interval, end_interval):
    '''
    Returns a list of utilization
    '''
    result = []
    for i in range(0, len(bytes_received_list)):
        bytes_received = bytes_received_list[i]
        if i == len(bytes_received_list) - 1:
            interval_size = (end_interval - start_interval) % SUBINTERVAL_SIZE
        else:
            interval_size = SUBINTERVAL_SIZE
        utilization = common_module.compute_utilization(bytes_received, bandwidth=BANDWIDTH, interval=SUBINTERVAL_SIZE)
        result.append(utilization)
    return result

def print_results(results):
    results.sort()
    for result in results:
        print result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('start_interval_index', type=int)
    parser.add_argument('end_interval_index', type=int)
    args = parser.parse_args()
    results = find_utilization_during_interval(args.root_dir, args.start_interval_index, args.end_interval_index)
    print_results(results)
