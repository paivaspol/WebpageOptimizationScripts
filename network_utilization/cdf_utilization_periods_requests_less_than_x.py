from argparse import ArgumentParser

import common_module
import dpkt
import simplejson as json
import os

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'

EXPECTED_BANDWIDTH = 6.0

def find_utilizations_during_intervals(intervals, initial_walltime, pcap_filename):
    # Precondition: assuming that the first interval is always have less requests than the threshold.
    # print 'intervals: ' + str(intervals)
    current_interval_index = 0
    current_interval = intervals[current_interval_index]
    end_walltime = intervals[len(intervals) - 1][1] + initial_walltime
    bytes_received_per_interval = []
    temp_intervals = list(intervals)
    exception_interrupted = False
    with open(pcap_filename, 'rb') as input_file:
        pcap_objects = dpkt.pcap.Reader(input_file)
        cumulative_bytes_received = 0
        try:
            for ts, buf in pcap_objects:
                if not initial_walltime <= ts <= end_walltime:
                    # Ignore packets before the initial walltime.
                    continue
                time_diff = ts - initial_walltime
                # print 'time_diff: {0} current interval: {1}'.format(time_diff, current_interval)
                    
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

                    if time_diff > current_interval[1]:
                        # print 'time diff: ' + str(time_diff) + ' changed from interval: ' + str(current_interval) + ' to: ' + str(intervals[current_interval_index + 1])
                        # Compute the bandwidth during the previous period.
                        bytes_received_per_interval.append(cumulative_bytes_received)
                        # Reset the variables
                        cumulative_bytes_received = 0
                        # Advance to the next interval
                        current_interval_index += 1
                        current_interval = intervals[current_interval_index]
                        # print 'current_interval: ' + str(current_interval)
                        while time_diff > current_interval[1]:
                            # print 'time diff: ' + str(time_diff) + ' changed from interval: ' + str(current_interval) + ' to: ' + str(intervals[current_interval_index + 1])
                            bytes_received_per_interval.append(0.0)
                            temp_intervals[current_interval_index] = None
                            current_interval_index += 1
                            current_interval = intervals[current_interval_index]
                    # print 'time diff: ' + str(time_diff) + ' current interval: ' + str(current_interval)
                    cumulative_bytes_received += ip.len
                    temp_intervals[current_interval_index] = None
                except AttributeError as e1:
                    # print 'attr error'
                    pass

        except dpkt.NeedData as e:
            print 'need data'
            exception_interrupted = True
            pass
        finally:
            # print 'cumulative_bytes_received: ' + str(cumulative_bytes_received)
            # print 'bytes_received_per_interval: ' + str(bytes_received_per_interval)
            # Handle the last case.
            bytes_received_per_interval.append(cumulative_bytes_received)
            temp_intervals[len(bytes_received_per_interval) - 1] = None
            while len(bytes_received_per_interval) < len(intervals) and not exception_interrupted:
                bytes_received_per_interval.append(0.0)
                temp_intervals[len(bytes_received_per_interval) - 1] = None

    # print 'bytes received per interval: ' + str(bytes_received_per_interval) + ' len: ' + str(len(bytes_received_per_interval))
    print 'temp intervals: ' + str(temp_intervals)
    # Fill in the gap.
    #if len(bytes_received_per_interval) != len(intervals):
    #    for i in range(0, len(temp_intervals)):
    #        if temp_intervals[i] is not None:
    #            bytes_received_per_interval.insert(i, 0.0)

    bandwidth_less_than_or_eq_x, bandwidth_greater_than_x = find_bandwidth_from_intervals(bytes_received_per_interval, intervals)
    return bandwidth_less_than_or_eq_x, bandwidth_greater_than_x

def convert_to_mbits(bytes_received):
    return bytes_received * 8e-6

def find_bandwidth_from_intervals(bytes_received_per_interval, intervals):
    print 'len bytes_received: {0} len intervals: {1}'.format(len(bytes_received_per_interval), len(intervals))
    result = []
    for i in range(0, len(bytes_received_per_interval)):
        time = (intervals[i][1] - intervals[i][0])
        # print 'time: ' + str(time)
        bandwidth = 1.0 * convert_to_mbits(bytes_received_per_interval[i]) / time
        result.append(bandwidth)
        # print 'mbits: {0} time: {1}'.format(bytes_received_per_interval[i], time)
    # print 'result: ' + str(result)
    bandwidth_less_than_or_eq_x = []
    bandwidth_greater_than_x = []
    for i in range(0, len(bytes_received_per_interval), 2):
        bandwidth_less_than_or_eq_x.append(result[i])
    for i in range(1, len(bytes_received_per_interval), 2):
        bandwidth_greater_than_x.append(result[i])
    return bandwidth_less_than_or_eq_x, bandwidth_greater_than_x

def find_periods_with_request_less_than_x(network_events, num_request_threshold, page_start_end_time, load_time):
    current_outstanding_requests = set()
    request_initial_timestamp = dict() # requestId --> timestamp
    initial_timestamp = None    # the first timestamp when there exists a request
    initial_walltime = None
    current_begin_interval = None
    intervals_requests_greater_than_x = []
    intervals_requests_less_than_or_eq_x = []
    for network_event in network_events:
        if network_event[METHOD] == 'Network.requestWillBeSent':
            # print 'method: {0} len: {1}'.format(network_event[METHOD], len(current_outstanding_requests))
            request_id = network_event[PARAMS][REQUEST_ID]
            current_outstanding_requests.add(request_id)
            timestamp = network_event[PARAMS]['timestamp']
            if current_begin_interval is None:
                current_begin_interval = timestamp
                initial_timestamp = timestamp
                initial_walltime = network_event[PARAMS]['wallTime']
            request_initial_timestamp[request_id] = timestamp
            if len(current_outstanding_requests) == num_request_threshold + 1:
                start_interval_diff = current_begin_interval - initial_timestamp
                end_interval_diff = timestamp - initial_timestamp
                if end_interval_diff - start_interval_diff > 1e-6:
                    intervals_requests_less_than_or_eq_x.append((start_interval_diff, end_interval_diff))
                    #print 'len: {0} start_interval_diff: {1} end_interval_diff: {2}'.format(len(current_outstanding_requests), start_interval_diff, end_interval_diff)
                    current_begin_interval = timestamp
        elif network_event[METHOD] == 'Network.loadingFinished':
            # print 'method: {0} len: {1}'.format(network_event[METHOD], len(current_outstanding_requests))
            current_outstanding_requests.remove(network_event[PARAMS][REQUEST_ID])
            # Check if the number of outstanding request falls under the threshold.
            if len(current_outstanding_requests) == num_request_threshold:
                request_id = network_event[PARAMS][REQUEST_ID]
                start_interval_diff = current_begin_interval - initial_timestamp
                end_interval_diff = timestamp - initial_timestamp
                if end_interval_diff - start_interval_diff > 1e-6:
                    intervals_requests_greater_than_x.append((start_interval_diff, end_interval_diff))
                    # print 'len: {0} start_interval_diff: {1} end_interval_diff: {2}'.format(len(current_outstanding_requests), start_interval_diff, end_interval_diff)
                    current_begin_interval = timestamp
                # print 'initial_walltime: {0} time diff: {1}'.format(request_initial_walltime[request_id], time_diff)

    # Handle the last case
    begin_interval_relative_time = current_begin_interval - initial_timestamp
    end_interval = network_events[len(network_events) - 1][PARAMS]['timestamp'] - initial_timestamp
    if len(current_outstanding_requests) <= num_request_threshold:
        intervals_requests_less_than_or_eq_x.append((begin_interval_relative_time, end_interval))
    else:
        intervals_requests_greater_than_x.append((begin_interval_relative_time, end_interval))

    # print 'intervals less than x: {0}'.format(intervals_requests_less_than_or_eq_x)
    # print 'intervals greater than x: {0}'.format(intervals_requests_greater_than_x)
    sorted_merged_list = sorted(intervals_requests_greater_than_x + intervals_requests_less_than_or_eq_x, key=lambda x: x[0])
    load_time = load_time / 1000.0
    last_interval = sorted_merged_list[len(sorted_merged_list) - 1]
    if last_interval[1] < load_time:
        sorted_merged_list[len(sorted_merged_list) - 1] = (last_interval[0], load_time)

    # print sorted_merged_list
    return sorted_merged_list, initial_walltime

# def print_intervals(intervals):
#     for interval in intervals:
#         print interval

# Returns a list of objectified network events.
def parse_network_events(network_events_filename):
    result = []
    with open(network_events_filename, 'rb') as input_file:
        for raw_line in input_file:
            result.append(json.loads(json.loads(raw_line.strip())))
    return result

def compute_utilization(bandwidth_list):
    utilization_list = []
    for bandwidth in bandwidth_list:
        utilization = bandwidth / EXPECTED_BANDWIDTH
        if utilization >= 1.0:
            print utilization
        else:
            utilization_list.append(utilization)
    return utilization_list

def output_to_file(output_directory, output_filename, utilization_list):
    output_full_path = os.path.join(output_directory, output_filename)
    with open(output_full_path, 'wb') as input_file:
        for utilization in utilization_list:
            input_file.write('{0}\n'.format(utilization))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('network_events_filename')
    parser.add_argument('page_start_end_time_filename')
    parser.add_argument('num_request_threshold', type=int)
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    network_events = parse_network_events(args.network_events_filename)
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time_filename)
    # print page_start_end_time
    load_time = page_start_end_time[1][1] - page_start_end_time[1][0]
    intervals, initial_walltime = find_periods_with_request_less_than_x(network_events, args.num_request_threshold, page_start_end_time, load_time)
    bandwidth_less_than_eq_x, bandwidth_greater_than_x = find_utilizations_during_intervals(intervals, initial_walltime, args.pcap_filename)
    utilization_less_than_eq_x = compute_utilization(bandwidth_less_than_eq_x)
    utilization_greater_than_x = compute_utilization(bandwidth_greater_than_x)
    output_to_file(args.output_dir, 'utilization_less_than_eq_x.txt', utilization_less_than_eq_x)
    output_to_file(args.output_dir, 'utilization_greater_than_x.txt', utilization_greater_than_x)
