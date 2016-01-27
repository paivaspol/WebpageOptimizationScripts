import argparse
import common_module
import dpkt
import struct
import os

def go_through_pcap(trace_filename, page_start_end_time):
    result = dict()
    with open(trace_filename, 'rb') as pcap_file:
        initial_timestamp = page_start_end_time[1][0]
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        window_scaling_option = 1
        try:
            for ts, buf in pcap_objects:
                #if not page_start_end_time[1][0] <= ts * 1000 <= page_start_end_time[1][1]:
                #    continue

                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    continue

                ip = eth.data
                try:
                    tcp = ip.data
                    if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or \
                        not common_module.check_web_port(True, tcp.dport):
                        continue
                    if window_scaling_option == 1:
                        options = dpkt.tcp.parse_opts(tcp.opts)
                        for option in options:
                            if option[0] == 3:
                                value, = struct.unpack('<b', bytearray(option[1]))
                                window_scaling_option = 2 ** value 
                    time_diff = (ts - (initial_timestamp / 1000))
                    window_size = tcp.win * window_scaling_option
                    if tcp.sport not in result:
                        result[tcp.sport] = []
                    result[tcp.sport].append((time_diff, tcp.win * window_scaling_option))
                except AttributeError as e:
                    pass
        except dpkt.NeedData as e1:
            pass
    return result

def write_cwdn_to_file(results, output_dir):
    for result in results:
        full_path = os.path.join(output_dir, 'cwnd_{0}.txt'.format(result))
        with open(full_path, 'wb') as output_file:
            for cwnd in results[result][1:]:
                output_file.write('{0:f} {1}\n'.format(cwnd[0], cwnd[1]))

def find_cwnd_in_directory(root_dir, output_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        url = common_module.extract_url_from_path(path)
        trace_filename = os.path.join(path, 'output.pcap')
        start_end_filename = os.path.join(path, 'start_end_time_' + url)
        page_start_end_time = common_module.parse_page_start_end_time(start_end_filename)
        results = go_through_pcap(trace_filename, page_start_end_time)
        output_path = os.path.join(output_dir, url)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        write_cwdn_to_file(results, output_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    find_cwnd_in_directory(args.root_dir, args.output_dir)
