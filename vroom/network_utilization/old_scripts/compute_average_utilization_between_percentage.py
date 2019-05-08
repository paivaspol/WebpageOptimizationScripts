from argparse import ArgumentParser

import dpkt

import common_module

def find_average_utilizations(page_start_end_time, pcap_filename, bytes_intervals):
    '''
    Finds the average utilization of each page within the specified bytes intervals.
    Returns a dictionary mapping from the page name to the average utilization.
    '''
    bytes_received = dict()
    time_usage = dict()
    with open(pcap_filename, 'rb') as trace_file:
        pcap_objects = dpkt.pcap.Reader(trace_file)
        current_interval_index = 0
        current_page = page_start_end_time[current_interval_index]
        current_page_interval = current_page[1]
        current_bytes_interval = bytes_intervals[current_interval_index]
        bytes_received[current_page[0]] = 0
        current_page_bytes = 0
        current_start_ts = None
        current_end_ts = None
        prev_ts = -1
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
                current_bytes_interval = bytes_intervals[current_interval_index]
                current_start_ts = None
                current_end_ts = None

            if not current_page_interval[0] <= ts <= current_page_interval[1] or \
                current_page_bytes > current_bytes_interval[1]:
                # timestamp not in the range that we are interested.
                # the number of bytes we have seen so far is out of the range we want.
                if current_page_bytes > current_bytes_interval[1] and \
                    current_end_ts is None:
                    current_end_ts = prev_ts
                    time_usage[current_page[0]] = current_end_ts - current_start_ts
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
            current_page_bytes += ip.len
            if current_bytes_interval[0] <= current_page_bytes <= current_bytes_interval[1]:
                if current_start_ts is None:
                    # if the start of the interval has not been set yet.
                    current_start_ts = ts
                bytes_received[current_page[0]] += ip.len # Updates the bytes for this page.
            prev_ts = ts

    return bytes_received, time_usage

def find_bytes_intervals(page_total_bytes_filename, start_percentage, end_percentage):
    '''
    Returns a list of tuples containing the page and the start and end percentages
    '''
    result = []
    start_percentage = 0.01 * start_percentage
    end_percentage = 0.01 * end_percentage
    with open(page_total_bytes_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.append((line[0], (start_percentage * int(line[1]), end_percentage * int(line[1]))))
    return result

if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument('page_start_end_time', help='The file containing the start and end time of each page')
    arg_parser.add_argument('page_total_bytes', help='Total bytes')
    arg_parser.add_argument('pcap_filename', help='The pcap filename')
    arg_parser.add_argument('start_percentage', type=int)
    arg_parser.add_argument('end_percentage', type=int)
    args = arg_parser.parse_args() 
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time)
    bytes_intervals = find_bytes_intervals(args.page_total_bytes, args.start_percentage, args.end_percentage)
    bytes_received, time_usage = find_bytes_received_and_time_usage(page_start_end_time, args.pcap_filename, bytes_interval)

