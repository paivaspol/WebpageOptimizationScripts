from argparse import ArgumentParser

import dpkt
import os

import common_module

def parse_pcap_file(pcap_filename, start_end_time, bytes_interval, total_bytes):
    time_first_bytes = None
    time_exceed_lower_bytes_threshold = None
    time_exceed_upper_bytes_threshold = None
    time_last_bytes = None
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
                tcp = ip.data
                if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                    continue
                cumulative_bytes += ip.len
                if cumulative_bytes >= 0 and time_first_bytes is None:
                    time_first_bytes = ts
                elif cumulative_bytes >= bytes_interval[0] and time_exceed_lower_bytes_threshold is None:
                    time_exceed_lower_bytes_threshold = ts
                elif cumulative_bytes >= bytes_interval[1] and time_exceed_upper_bytes_threshold is None:
                    time_exceed_upper_bytes_threshold = ts
                elif cumulative_bytes >= total_bytes and time_last_bytes is None:
                    time_last_bytes = ts
        except dpkt.NeedData as e:
            pass
    return (start_end_time[1][0], time_first_bytes, time_exceed_lower_bytes_threshold, time_exceed_upper_bytes_threshold, time_last_bytes, start_end_time[1][1])

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
    full_path = os.path.join(output_dir, 'interval_border.txt')
    if None not in result:
        with open(full_path, 'wb') as output_file:
            output_file.write('{0:f} {1:f} {2:f} {3:f} {4:f} {5:f}\n'.format(result[0], result[1], result[2], result[3], result[4], result[5]))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('start_end_page_load')
    parser.add_argument('total_bytes_filename')
    parser.add_argument('percent_bytes_ignoring', type=int)
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    page_load_interval = common_module.parse_page_start_end_time(args.start_end_page_load)
    bytes_interval, total_bytes = get_bytes_interval(args.total_bytes_filename, args.percent_bytes_ignoring)
    interval_limits = parse_pcap_file(args.pcap_filename, page_load_interval, bytes_interval, total_bytes)
    output_to_file(interval_limits, args.output_dir)
