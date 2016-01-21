from argparse import ArgumentParser

import common_module
import dpkt
import simplejson as json
import os
import numpy

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'

EXPECTED_BANDWIDTH = 6.0

def find_utilizations_during_intervals(intervals, initial_walltime, pcap_filename, max_requests_each_interval, num_requests_threshold):
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

    bandwidth_less_than_or_eq_x, bandwidth_greater_than_x = find_bandwidth_from_intervals(bytes_received_per_interval, intervals, max_requests_each_interval, num_requests_threshold)
    return bandwidth_less_than_or_eq_x, bandwidth_greater_than_x

def convert_to_mbits(bytes_received):
    return bytes_received * 8e-6

def find_bandwidth_from_intervals(bytes_received_per_interval, intervals, max_requests_during_interval, num_requests_threshold):
    print 'len bytes_received: {0} len intervals: {1}'.format(len(bytes_received_per_interval), len(intervals))
    bandwidth_less_than_or_eq_x = []
    bandwidth_greater_than_x = []
    sorted_max_requests_during_interval = sorted(max_requests_during_interval.items(), key=lambda x: x[0][0])
    for i in range(0, len(bytes_received_per_interval)):
        interval = sorted_max_requests_during_interval[i][0]
        time = (interval[1] - interval[0])
        if time > 0:
            # print 'time: ' + str(time)
            bandwidth = 1.0 * convert_to_mbits(bytes_received_per_interval[i]) / time
            if bandwidth == 0.0:
                print '0-bandwidth: ' + str(interval) + ' bytes_received_per_interval[i] ' + str(bytes_received_per_interval[i])
            if max_requests_during_interval[interval] > num_requests_threshold:
                bandwidth_greater_than_x.append(bandwidth)
            elif max_requests_during_interval[interval] <= num_requests_threshold:
                bandwidth_less_than_or_eq_x.append(bandwidth)
            # print 'mbits: {0} time: {1}'.format(bytes_received_per_interval[i], time)
    # print 'result: ' + str(result)
    return bandwidth_less_than_or_eq_x, bandwidth_greater_than_x

def find_periods_with_request_less_than_x(network_events, num_request_threshold, page_start_end_time, load_time):
    current_outstanding_requests = set()
    request_initial_timestamp = dict() # requestId --> timestamp
    initial_timestamp = None    # the first timestamp when there exists a request
    initial_walltime = None
    current_begin_interval = None
    current_max_num_outstanding_request_during_interval = -1
    current_interval_requests = set()
    intervals_requests_greater_than_x = []
    intervals_requests_less_than_or_eq_x = []
    requests_during_interval = dict()   # This is a mapping from the interval to a set of requestIds during that interval.
    max_requests_during_interval = dict()   # Maps from the request id to the max number of requests during the interval.
    for network_event in network_events:
        if network_event[METHOD] == 'Network.requestWillBeSent':
            # print 'method: {0} len: {1}'.format(network_event[METHOD], len(current_outstanding_requests))
            request_id = network_event[PARAMS][REQUEST_ID]
            timestamp = network_event[PARAMS]['timestamp']
            request_initial_timestamp[request_id] = timestamp

            if current_begin_interval is None:
                current_begin_interval = timestamp
                initial_timestamp = timestamp
                initial_walltime = network_event[PARAMS]['wallTime']

            # The request is not in the current outstanding requests.
            # Check if adding the requests will make the number of outstanding request exceeds the threshold.
            if request_id not in current_outstanding_requests and len(current_outstanding_requests) + 1 == num_request_threshold + 1:
                # print 'going above: current_outstanding_requests: ' + str(len(current_outstanding_requests))
                start_interval_diff = current_begin_interval - initial_timestamp
                end_interval_diff = timestamp - initial_timestamp
                #if end_interval_diff - start_interval_diff > 0:
                interval = (start_interval_diff, end_interval_diff)
                intervals_requests_less_than_or_eq_x.append(interval)
                # print 'len: {0} start_interval_diff: {1} end_interval_diff: {2}'.format(len(current_outstanding_requests), start_interval_diff, end_interval_diff)
                current_begin_interval = timestamp
                requests_during_interval[interval] = list(current_interval_requests)
                max_requests_during_interval[interval] = current_max_num_outstanding_request_during_interval
                current_max_num_outstanding_request_during_interval = len(current_outstanding_requests) + 1
                current_interval_requests = set(current_outstanding_requests)
            
            current_outstanding_requests.add(request_id)
            current_interval_requests.add(request_id)
            print 'current outstanding requests: ' + str(len(current_outstanding_requests))
        elif network_event[METHOD] == 'Network.loadingFinished':
            # print 'method: {0} len: {1}'.format(network_event[METHOD], len(current_outstanding_requests))

            # The request is in the current outstanding requests.
            # Check if removing the requests will make the number of outstanding request falls under the threshold.
            request_id = network_event[PARAMS][REQUEST_ID]
            timestamp = network_event[PARAMS]['timestamp']
            print 'request: ' + str(request_id) + ' request started: ' + str(request_initial_timestamp[request_id] - initial_timestamp) + ' time: ' + str(timestamp - initial_timestamp)

            if request_id in current_outstanding_requests and len(current_outstanding_requests) - 1 == num_request_threshold:
                print 'going below: current_outstanding_requests: ' + str(len(current_outstanding_requests))
                start_interval_diff = current_begin_interval - initial_timestamp
                end_interval_diff = timestamp - initial_timestamp
                #if end_interval_diff - start_interval_diff > 0:
                interval = (start_interval_diff, end_interval_diff)
                intervals_requests_greater_than_x.append(interval)
                requests_during_interval[interval] = list(current_interval_requests)
                # print 'len: {0} start_interval_diff: {1} end_interval_diff: {2}'.format(len(current_outstanding_requests), start_interval_diff, end_interval_diff)
                current_begin_interval = timestamp
                max_requests_during_interval[interval] = current_max_num_outstanding_request_during_interval
                current_max_num_outstanding_request_during_interval = len(current_outstanding_requests) - 1
                current_interval_requests = set(current_outstanding_requests)
                # print 'initial_walltime: {0} time diff: {1}'.format(request_initial_walltime[request_id], time_diff)
            # Actually remove the request.
            current_outstanding_requests.remove(request_id)
            print 'current outstanding requests: ' + str(len(current_outstanding_requests))
        current_max_num_outstanding_request_during_interval = max(current_max_num_outstanding_request_during_interval, len(current_outstanding_requests))

    # Handle the last case
    begin_interval_relative_time = current_begin_interval - initial_timestamp
    end_interval = network_events[len(network_events) - 1][PARAMS]['timestamp'] - initial_timestamp
    interval = (begin_interval_relative_time, end_interval)
    if len(current_outstanding_requests) <= num_request_threshold:
        intervals_requests_less_than_or_eq_x.append(interval)
    else:
        intervals_requests_greater_than_x.append(interval)
    requests_during_interval[interval] = list(current_outstanding_requests)
    max_requests_during_interval[interval] = current_max_num_outstanding_request_during_interval

    # print 'intervals less than x: {0}'.format(intervals_requests_less_than_or_eq_x)
    # print 'intervals greater than x: {0}'.format(intervals_requests_greater_than_x)
    sorted_merged_list = sorted(intervals_requests_greater_than_x + intervals_requests_less_than_or_eq_x, key=lambda x: x[0])
    load_time = load_time / 1000.0
    last_interval = sorted_merged_list[len(sorted_merged_list) - 1]
    if last_interval[1] < load_time:
        sorted_merged_list[len(sorted_merged_list) - 1] = (last_interval[0], load_time)

    # print sorted_merged_list
    return sorted_merged_list, initial_walltime, requests_during_interval, max_requests_during_interval

# Returns a list of objectified network events.
def parse_network_events(network_events_filename):
    result = []
    with open(network_events_filename, 'rb') as input_file:
        for raw_line in input_file:
            result.append(json.loads(json.loads(raw_line.strip())))
    return result

def compute_utilization(bandwidth_list):
    '''
    Computes the utilization
    '''
    utilization_list = []
    for bandwidth in bandwidth_list:
        utilization = bandwidth / EXPECTED_BANDWIDTH
        if utilization >= 1.0:
            print utilization
        else:
            utilization_list.append(utilization)
    return utilization_list

def read_request_sizes(page_request_size_filename):
    '''
    Reads and parses the request sizes from the file.
    Returns a dictionary mapping from the Request Id to the request size.
    '''
    result = dict()
    with open(page_request_size_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

def find_request_size_stat_per_interval(interval_to_requests_dict, request_sizes_dict, max_requests_during_interval, num_requests_threshold, stat='median', which_interval='greater'):
    '''
    Returns a list containing the median/max/min object size of each interval.
    '''
    result = []
    for interval in max_requests_during_interval:
        requests_list = interval_to_requests_dict[interval]
        object_size_list = generate_object_size_list(requests_list, request_sizes_dict)
        if which_interval == 'less_than_equal' and max_requests_during_interval[interval] <= num_requests_threshold or \
            which_interval == 'greater' and max_requests_during_interval[interval] > num_requests_threshold:
            # print 'interval: ' + str(interval) + ' object_size_list: ' + str(object_size_list) + ' requests_list: ' + str(requests_list)
            stat_value = find_stat_value(object_size_list, stat)
            if stat_value > 0:
                result.append(stat_value)
    return result

def find_stat_value(object_size_list, stat):
    '''
    Finds the stat value from the list.
    '''
    stat_value = -1
    try:
        if stat == 'median':
                stat_value = numpy.median(object_size_list)
        elif stat == 'max':
            stat_value = max(object_size_list)
    except Exception as e:
        pass
    return stat_value

def generate_object_size_list(requests_list, request_to_object_size_dict):
    '''
    Returns a list containing the object sizes.
    '''
    result = []
    for request in requests_list:
        result.append(request_to_object_size_dict[request])
    return result

def output_list_to_file(output_directory, output_filename, utilization_list):
    output_full_path = os.path.join(output_directory, output_filename)
    with open(output_full_path, 'wb') as input_file:
        for utilization in utilization_list:
            input_file.write('{0}\n'.format(utilization))

def print_intervals(output_directory, threshold, max_requests_during_interval, requests_during_interval):
    full_path = os.path.join(output_directory, 'intervals_less_than_{0}.txt'.format(threshold))
    with open(full_path, 'wb') as output_file:
        sorted_max_requests_during_interval = sorted(max_requests_during_interval.items(), key=lambda x: x[0][0])
        for i in range(0, len(max_requests_during_interval)):
            interval = sorted_max_requests_during_interval[i][0]
            # print 'max req: {0} len req: {1}'.format(max_requests_during_interval[interval], len(requests_during_interval[interval]))
            output_file.write('{0} {1} {2} {3} {4}\n'.format((i % 2), interval[0], interval[1], max_requests_during_interval[interval], sorted(requests_during_interval[interval])))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('network_events_filename')
    parser.add_argument('page_start_end_time_filename')
    parser.add_argument('page_request_size_filename')
    parser.add_argument('num_request_threshold', type=int)
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    network_events = parse_network_events(args.network_events_filename)
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time_filename)
    request_sizes_dict = read_request_sizes(args.page_request_size_filename)
    # print page_start_end_time
    load_time = page_start_end_time[1][1] - page_start_end_time[1][0]
    intervals, initial_walltime, requests_during_interval, max_requests_during_interval = find_periods_with_request_less_than_x(network_events, args.num_request_threshold, page_start_end_time, load_time)
    print_intervals(args.output_dir, args.num_request_threshold, max_requests_during_interval, requests_during_interval)

    # Find the bandwidth and utilizations during those intervals
    bandwidth_less_than_eq_x, bandwidth_greater_than_x = find_utilizations_during_intervals(intervals, initial_walltime, args.pcap_filename, max_requests_during_interval, args.num_request_threshold)
    utilization_less_than_eq_x = compute_utilization(bandwidth_less_than_eq_x)
    utilization_greater_than_x = compute_utilization(bandwidth_greater_than_x)
    output_list_to_file(args.output_dir, 'utilization_less_than_eq_x.txt', utilization_less_than_eq_x)
    output_list_to_file(args.output_dir, 'utilization_greater_than_x.txt', utilization_greater_than_x)

    # Request sizes.
    median_requests_sizes_intervals_greater_than_x = find_request_size_stat_per_interval(requests_during_interval, request_sizes_dict, max_requests_during_interval, args.num_request_threshold, stat='median', which_interval='greater')
    output_list_to_file(args.output_dir, 'median_request_sizes_intervals_greater.txt', median_requests_sizes_intervals_greater_than_x)
    max_requests_sizes_intervals_greater_than_x = find_request_size_stat_per_interval(requests_during_interval, request_sizes_dict, max_requests_during_interval, args.num_request_threshold, stat='max', which_interval='greater')
    output_list_to_file(args.output_dir, 'max_request_sizes_intervals_greater.txt', max_requests_sizes_intervals_greater_than_x)
    median_requests_sizes_intervals_less_than_eq_x = find_request_size_stat_per_interval(requests_during_interval, request_sizes_dict, max_requests_during_interval, args.num_request_threshold, stat='median', which_interval='less_than_equal')
    output_list_to_file(args.output_dir, 'median_request_sizes_intervals_less.txt', median_requests_sizes_intervals_less_than_eq_x)
    max_requests_sizes_intervals_less_than_eq_x = find_request_size_stat_per_interval(requests_during_interval, request_sizes_dict, max_requests_during_interval, args.num_request_threshold, stat='max', which_interval='less_than_equal')
    output_list_to_file(args.output_dir, 'max_request_sizes_intervals_less.txt', max_requests_sizes_intervals_less_than_eq_x)
