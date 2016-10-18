from argparse import ArgumentParser

import dpkt
import os

import common_module

def parse_pcap_file(pcap_filename, start_end_time, bytes_thresholds):
    result = []
    result.append(start_end_time[1][0]) # Start of load process
    bytes_threshold_index = 0
    with open(pcap_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        cumulative_bytes = 0
        try:
            for ts, buf in pcap_objects:
                ts = ts * 1000
                if not start_end_time[1][0] <= ts <= start_end_time[1][1]:
                    continue

                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    # Only use IP packets 
                    continue

                ip = eth.data
                try:
                    tcp = ip.data
                    if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                        continue
                    cumulative_bytes += ip.len
                    if cumulative_bytes > bytes_thresholds[bytes_threshold_index]:
                        result.append(ts)
                        bytes_threshold_index += 1
                except Exception as e1:
                    pass
        except dpkt.NeedData as e:
            pass
    result.append(start_end_time[1][1])
    return result

def get_bytes_thresholds(total_bytes_filename, percent_bytes_ignoring):
    '''
    Returns a list containing the bytes thresholds
    '''
    total_bytes = None
    with open(total_bytes_filename, 'rb') as input_file:
        total_bytes = int(input_file.readline().strip())
    result = []
    bytes_per_interval = int((percent_bytes_ignoring / 100.0) * total_bytes)
    expected_num_intervals = (100 / percent_bytes_ignoring) + 1
    cumulative_bytes = 0
    while cumulative_bytes < total_bytes:
        result.append(cumulative_bytes)
        cumulative_bytes += bytes_per_interval
    if len(result) < expected_num_intervals:
        result.append(total_bytes)
    return result

def get_bytes_interval(total_bytes_filename, percent_bytes_ignoring):
    '''
    Parses the total bytes
    '''
    total_bytes = None
    with open(total_bytes_filename, 'rb') as input_file:
        total_bytes = int(input_file.readline().strip())
    bytes_ignoring = int((percent_bytes_ignoring / 100.0) * total_bytes)
    start_interval = bytes_ignoring
    end_interval = total_bytes - bytes_ignoring
    return (start_interval, end_interval), total_bytes

def output_to_file(result, output_dir):
    full_path = os.path.join(output_dir, 'interval_border_evenly_breakdown.txt')
    if None not in result:
        with open(full_path, 'wb') as output_file:
            output_file.write(construct_output_string(result) + '\n')

def construct_output_string(result):
    retval = ''
    for ts in result:
        retval += '{0:f} '.format(ts)
    return retval.strip()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('start_end_page_load')
    parser.add_argument('total_bytes_filename')
    parser.add_argument('percent_bytes_per_interval', type=int)
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    page_load_interval = common_module.parse_page_start_end_time(args.start_end_page_load)
    bytes_thresholds = get_bytes_thresholds(args.total_bytes_filename, args.percent_bytes_per_interval)
    # bytes_interval, total_bytes = get_bytes_interval(args.total_bytes_filename, args.percent_bytes_ignoring)
    interval_limits = parse_pcap_file(args.pcap_filename, page_load_interval, bytes_thresholds)
    output_to_file(interval_limits, args.output_dir)
