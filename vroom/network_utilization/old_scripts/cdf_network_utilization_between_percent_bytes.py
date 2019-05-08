from argparse import ArgumentParser

import common_module

import dpkt
import os

DOWNLOAD_BANDWIDTH = 4.0

def find_bandwidth(base_dir, bytes_range, use_spdyproxy):
    # print 'base_dir: ' + base_dir
    trace_full_path = os.path.join(base_dir, 'output.pcap')
    page_start_end_time = os.path.join(base_dir, 'start_end_time_{0}'.format(common_module.extract_url_from_path(base_dir)))
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
                if not (int(ip.p) == int(dpkt.ip.IP_PROTO_TCP) and common_module.check_web_port(use_spdyproxy, tcp.sport)) or \
                    not (int(ip.p) == int(dpkt.ip.IP_PROTO_UDP) and common_module.check_web_port(use_spdyproxy, udp.sport)):
                    
                    # We only care about HTTP or HTTPS or using SPDYProxy
                    continue
                bytes_received += ip.len
                if start_ts is None and bytes_received >= bytes_range[0]:
                    start_ts = ts
                elif end_ts is None and bytes_received >= bytes_range[1]:
                    # Out of the bytes range and break out of the loop.
                    end_ts = ts
                    break
            except Exception as e:
                exception_counter += 1
                pass
        time_spent = end_ts - start_ts
        # print 'dir: {0} exceptions: {1}'.format(base_dir, exception_counter)
        # print 'Bytes received: {0} Mbits received: {1} time spent: {2}'.format(bytes_received, convert_to_mbits(bytes_received), time_spent)
    return 1.0 * convert_to_mbits(bytes_received) / time_spent

def convert_to_mbits(bytes_received):
    return bytes_received * 8e-6

def get_byte_range(base_dir, lower_percentage, upper_percentage):
    '''
    Returns the bytes range.
    '''
    full_path = os.path.join(base_dir, 'bytes_received.txt')
    with open(full_path, 'rb') as input_file:
        total_bytes_received = int(input_file.readline())
        lower_bytes = (lower_percentage * total_bytes_received) / 100.0
        upper_bytes = (upper_percentage * total_bytes_received) / 100.0
        bytes_range = (lower_bytes, upper_bytes)
        #print bytes_range
        return bytes_range

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('base_dir')
    parser.add_argument('lower_percentage', type=int)
    parser.add_argument('upper_percentage', type=int)
    parser.add_argument('--use-spdyproxy', action='store_true', default=False)
    args = parser.parse_args()
    byte_range = get_byte_range(args.base_dir, args.lower_percentage, args.upper_percentage)
    bandwidth = find_bandwidth(args.base_dir, byte_range, args.use_spdyproxy)
    if bandwidth > DOWNLOAD_BANDWIDTH:
        print 'exceed: ' + args.base_dir
    else:
        print '{0}'.format(bandwidth / DOWNLOAD_BANDWIDTH)

