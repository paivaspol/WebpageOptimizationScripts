from argparse import ArgumentParser

import dpkt
import os

import common_module

def find_total_bytes(page_start_end_time, pcap_filename, use_spdyproxy):
    '''
    Finds the total bytes of each page.
    '''
    bytes_received = 0
    with open(pcap_filename, 'rb') as trace_file:
        pcap_objects = dpkt.pcap.Reader(trace_file)
        current_page_interval = common_module.parse_page_start_end_time(page_start_end_time)[1]
        print 'current interval: ' + str(current_page_interval)
        try:
            for ts, buf in pcap_objects:
                ts = ts * 1000
                if not current_page_interval[0] <= ts <= current_page_interval[1]:
                    # timestamp not in the range that we are interested.
                    continue

                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    # Only use IP packets 
                    continue

                ip = eth.data
                tcp = ip.data
                if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or not common_module.check_web_port(use_spdyproxy, tcp.sport):
                    # We only care about HTTP or HTTPS
                    continue
                bytes_received += ip.len # Updates the bytes for this page.
        except Exception as e:
            pass
    print 'bytes: {0}'.format(bytes_received)
    return bytes_received

def output_result(result, output_filename):
    '''
    Outputs the result.
    '''
    with open(output_filename, 'wb') as output_file:
        output_file.write('{0}\n'.format(result))

def find_bytes_wrapper(root_dir, use_spdyproxy, output_filename='bytes_received.txt'):
    for path, _, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            continue
        page_start_end_time = os.path.join(path, 'start_end_time_{0}'.format(common_module.extract_url_from_path(path)))
        pcap_filename = os.path.join(path, 'output.pcap')
        output_filename_full_path = os.path.join(path, output_filename)
        print 'Getting bytes in {0}'.format(path)
        if os.path.exists(page_start_end_time) and os.path.exists(pcap_filename):
            bytes_received = find_total_bytes(page_start_end_time, pcap_filename, use_spdyproxy)
            output_result(bytes_received, output_filename_full_path)

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('root_dir')
    arg_parser.add_argument('--use-spdyproxy', action='store_true', default=False)
    args = arg_parser.parse_args()
    find_bytes_wrapper(args.root_dir, args.use_spdyproxy)
