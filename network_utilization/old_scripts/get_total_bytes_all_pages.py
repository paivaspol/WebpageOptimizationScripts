from argparse import ArgumentParser

import dpkt

import common_module

def find_total_bytes(page_start_end_time, pcap_filename):
    '''
    Finds the total bytes of each page.
    '''
    bytes_received = dict()
    with open(pcap_filename, 'rb') as trace_file:
        pcap_objects = dpkt.pcap.Reader(trace_file)
        current_interval_index = 0
        current_page = page_start_end_time[current_interval_index]
        current_page_interval = current_page[1]
        bytes_received[current_page[0]] = 0
        for ts, buf in pcap_objects:
            ts = ts * 1000
            if ts > current_page_interval[1]:
                # timestamp is already greater than the current page interval
                # advance the current page interval.
                current_interval_index += 1
                if current_interval_index >= len(page_start_end_time):
                    # There isn't any page left. Break out.
                    break
                current_page = page_start_end_time[current_interval_index]
                current_page_interval = current_page[1]
                bytes_received[current_page[0]] = 0

            if not current_page_interval[0] <= ts <= current_page_interval[1]:
                # timestamp not in the range that we are interested.
                continue

            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                # Only use IP packets 
                continue

            ip = eth.data
            tcp = ip.data
            if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                # We only care about HTTP or HTTPS
                continue
            bytes_received[current_page[0]] += ip.len # Updates the bytes for this page.
    return bytes_received   


def output_result(result):
    '''
    Outputs the result.
    '''
    for page in result:
        print '{0} {1}'.format(page, result[page])

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('page_start_end_time', help='The file containing the start and end time of each page')
    arg_parser.add_argument('pcap_file', help='The pcap file.')
    args = arg_parser.parse_args()
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time)
    bytes_received = find_total_bytes(page_start_end_time, args.pcap_file)
    output_result(bytes_received)
