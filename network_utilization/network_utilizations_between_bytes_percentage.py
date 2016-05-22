from argparse import ArgumentParser

import common_module

import dpkt
import os
import numpy

INTERVAL_SIZE = 100

def process_pages(root_dir, lower_percentage, upper_percentage, use_spdyproxy):
    pages = os.listdir(root_dir)
    for page in pages:
        bytes_range = get_byte_range(root_dir, page, lower_percentage, upper_percentage)
        find_bandwidth(root_dir, page, bytes_range, use_spdyproxy)

def find_time_interval(base_dir, page, bytes_range, use_spdyproxy):
    # print 'base_dir: ' + base_dir
    trace_full_path = os.path.join(base_dir, page, 'output.pcap')
    page_start_end_time = os.path.join(base_dir, page, 'start_end_time_{0}'.format(page))
    current_page_interval = common_module.parse_page_start_end_time(page_start_end_time)[1]
    with open(trace_full_path, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        start_ts = None
        end_ts = None
        bytes_received = 0
        exception_counter = 0
        for ts, buf in pcap_objects:
            if not current_page_interval[0] <= ts * 1000 <= current_page_interval[1]:
                # timestamp not in the range that we are interested.
                continue
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                # Only use IP packets 
                continue
            ip = eth.data
            try:
                tcp = ip.data
                if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or not common_module.check_web_port(use_spdyproxy, tcp.sport):
                    # We only care about HTTP or HTTPS or using SPDYProxy
                    continue
                bytes_received += ip.len
                if start_ts is None and bytes_received >= bytes_range[0]:
                    start_ts = ts * 1000
                elif end_ts is None and bytes_received >= bytes_range[1]:
                    # Out of the bytes range and break out of the loop.
                    end_ts = ts * 1000
                    break
            except Exception as e:
                exception_counter += 1
                pass
        return start_ts, end_ts

def find_bandwidth(base_dir, page, bytes_range, use_spdyproxy):
    # print 'base_dir: ' + base_dir
    trace_full_path = os.path.join(base_dir, page, 'output.pcap')
    page_start_end_time = os.path.join(base_dir, page, 'start_end_time_{0}'.format(page))
    current_page_interval = common_module.parse_page_start_end_time(page_start_end_time)[1]
    start_ts, end_ts = find_time_interval(base_dir, page, bytes_range, use_spdyproxy)
    if start_ts is None and end_ts is None:
        return
    bytes_received_slots = generate_utilization_slots(start_ts, end_ts)
    with open(trace_full_path, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        try:
            for ts, buf in pcap_objects:
                ts = ts * 1000
                if not start_ts <= ts <= end_ts:
                    # timestamp not in the range that we are interested.
                    continue
                utilization_index = int(ts - start_ts) / INTERVAL_SIZE
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    # Only use IP packets 
                    continue
                ip = eth.data
                try:
                    tcp = ip.data
                    if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or not common_module.check_web_port(use_spdyproxy, tcp.sport):
                        # We only care about HTTP or HTTPS or using SPDYProxy
                        continue
                    bytes_received_slots[utilization_index] += ip.len
                except Exception as e:
                    pass
        except Exception as e2:
            pass
    utilizations = compute_utilizations(bytes_received_slots)
    median_utilization = numpy.median(utilizations)
    max_utilization = max(utilizations)
    print '{0} {1} {2}'.format(page, median_utilization, max_utilization)

def compute_utilizations(bytes_received_per_interval):
    utilizations = []
    for bytes_received in bytes_received_per_interval:
        utilization = convert_to_mbits(bytes_received) / (args.expected_bandwidth * (0.1)) # each 100ms can handle 6mbps * 0.1(s/100ms) = 0.6 mbits
        utilizations.append(utilization)
    return utilizations

def generate_utilization_slots(start_ts, end_ts):
    total_time = end_ts - start_ts
    num_slots = int(total_time) / INTERVAL_SIZE
    if total_time % INTERVAL_SIZE != 0:
        num_slots += 1
    utilization_slots = []
    for i in range(0, int(num_slots)):
        utilization_slots.append(0.0)
    return utilization_slots

def convert_to_mbits(bytes_received):
    return bytes_received * 8e-6

def get_byte_range(base_dir, page, lower_percentage, upper_percentage):
    '''
    Returns the bytes range.
    '''
    full_path = os.path.join(base_dir, page, 'bytes_received.txt')
    with open(full_path, 'rb') as input_file:
        total_bytes_received = int(input_file.readline())
        lower_bytes = 1.0 * (lower_percentage * total_bytes_received) / INTERVAL_SIZE
        upper_bytes = 1.0 * (upper_percentage * total_bytes_received) / INTERVAL_SIZE
        bytes_range = (lower_bytes, upper_bytes)
        #print bytes_range
        return bytes_range

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('base_dir')
    parser.add_argument('lower_percentage', type=int)
    parser.add_argument('upper_percentage', type=int)
    parser.add_argument('expected_bandwidth', type=float)
    parser.add_argument('--use-spdyproxy', action='store_true', default=False)
    args = parser.parse_args()
    process_pages(args.base_dir, args.lower_percentage, args.upper_percentage, args.use_spdyproxy)

