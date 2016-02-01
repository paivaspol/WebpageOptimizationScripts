from argparse import ArgumentParser

import common_module
import dpkt
import simplejson as json
import os

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
EXPECTED_BANDWIDTH = 6.0

def find_utilization_for_intervals(pcap_filename, intervals, page_load_start_end):
    current_interval_index = 0
    current_interval = intervals[current_interval_index]
    interval_to_bytes_received = generate_interval_to_num_request_dict(intervals)
    with open(pcap_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        try:
            for ts, buf in pcap_objects:
                ts = ts * 1000
                if not page_load_start_end[0] <= ts <= page_load_start_end[1]:
                    continue

                if ts >= current_interval[1]:
                    # Advance the current interval
                    current_interval_index += 1
                    current_interval = intervals[current_interval_index]
                
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    # Only use IP packets.
                    continue
                
                ip = eth.data
                try:
                    tcp = ip.data
                    if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or not common_module.check_web_port(True, tcp.sport): # True for spdyproxy
                        # We only care about HTTP or HTTPS
                        continue
                    interval_to_bytes_received[current_interval] += ip.len
                except AttributeError as e1:
                    pass
        except dpkt.NeedData as e:
            pass
    return find_utilizations(interval_to_bytes_received), interval_to_bytes_received

def find_utilizations(interval_to_bytes):
    result = dict()
    for interval in interval_to_bytes:
        mbits_received = common_module.convert_to_mbits(interval_to_bytes[interval])
        time_in_seconds = ((interval[1] - interval[0]) / 1000)
        bandwidth = mbits_received / time_in_seconds
        result[interval] = bandwidth / EXPECTED_BANDWIDTH
    return result

def find_requests_for_intervals(network_events, intervals, requests_to_ignore):
    interval_to_num_requests = generate_interval_to_requests_dict(intervals)
    request_to_load_interval_dict = dict() # maps from the request id to the interval.
    request_initial_walltime = dict()
    request_initial_timestamp = dict()
    for network_event in network_events:
        if 'timestamp' not in network_event[PARAMS]:
            continue
        request_id = network_event[PARAMS][REQUEST_ID]
        if request_id in requests_to_ignore:
            continue
        timestamp = network_event[PARAMS]['timestamp'] * 1000 # Convert to ms
        if network_event[METHOD] == 'Network.requestWillBeSent':
            request_initial_walltime[request_id] = network_event[PARAMS]['wallTime'] * 1000 # Convert to ms
            request_initial_timestamp[request_id] = timestamp
        elif network_event[METHOD] == 'Network.loadingFinished':
            request_load_interval = (request_initial_walltime[request_id], request_initial_walltime[request_id] + (timestamp - request_initial_timestamp[request_id]))
            request_to_load_interval_dict[request_id] = request_load_interval
    for request_id in request_to_load_interval_dict:
        request_load_interval = request_to_load_interval_dict[request_id]
        # print 'request id: ' + str(request_id) + ' load interval: ' + str(request_load_interval) + ' load time: ' + str(request_load_interval[1] - request_load_interval[0])
        populate_num_requests_for_all_intervals(interval_to_num_requests, request_load_interval, request_id)
    return interval_to_num_requests

def populate_num_requests_for_all_intervals(interval_to_num_request_dict, request_load_interval, request_id):
    for interval in interval_to_num_request_dict:
        # if request_load_interval[0] <= interval[0] < interval[1] <= request_load_interval[1] or \
        #     request_load_interval[0] <= interval[0] <= request_load_interval[1] < interval[1] or \
        #     interval[0] <= request_load_interval[0] <= interval[1] < request_load_interval[1] or \
        #if interval[0] <= request_load_interval[0] < request_load_interval[1] <= interval[1]:
        if request_load_interval[0] < interval[0] < interval[1] < request_load_interval[1]:
            # print '\t[OK] interval: {0} request interval: {1}'.format(interval, request_load_interval)
            interval_to_num_request_dict[interval].add(request_id)

def generate_interval_to_num_request_dict(intervals):
    result = dict()
    for interval in intervals:
        result[interval] = 0
    return result

def generate_interval_to_requests_dict(intervals):
    result = dict()
    for interval in intervals:
        result[interval] = set()
    return result
            
def split_page_load_to_intervals(page_start_end_time, interval_size=100):
    '''
    Splits the page load time into 100ms intervals, except the last interval.
    '''
    result = []
    start_load_time, end_load_time = page_start_end_time[1]
    start_interval = start_load_time
    end_interval = start_load_time + interval_size
    while start_interval < end_load_time:
        interval = (start_interval, end_interval)
        result.append(interval)
        start_interval = end_interval
        end_interval = min(end_interval + interval_size, end_load_time)
    return result

def output_to_file(result, utilizations, intervals_to_bytes_received, output_dir, interval_size):
    full_path = os.path.join(output_dir, '{0}ms_interval_num_request.txt'.format(interval_size))
    with open(full_path, 'wb') as output_file:
        for interval in result:
            requests = result[interval]
            line = '{0:f} {1:f} {2} {3} {4:f}'.format(interval[0], interval[1], len(requests), intervals_to_bytes_received[interval], utilizations[interval])
            for request in requests:
                line += ' ' + str(request)
            output_file.write(line + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_events_filename')
    parser.add_argument('page_start_end_time_filename')
    parser.add_argument('pcap_filename')
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--requests-to-ignore', default=None)
    parser.add_argument('--interval-size', default=100, type=int)
    args = parser.parse_args()
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time_filename)
    requests_to_ignore = common_module.parse_requests_to_ignore_in_url_directory(args.requests_to_ignore)
    page_load_intervals = split_page_load_to_intervals(page_start_end_time, args.interval_size)
    network_events = common_module.parse_network_events(args.network_events_filename)
    interval_to_request_count = find_requests_for_intervals(network_events, page_load_intervals, requests_to_ignore)
    utilizations, intervals_to_bytes_received = find_utilization_for_intervals(args.pcap_filename, page_load_intervals, page_start_end_time[1])
    output_to_file(interval_to_request_count, utilizations, intervals_to_bytes_received, args.output_dir, args.interval_size)
