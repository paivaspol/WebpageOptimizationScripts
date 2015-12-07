import argparse
import dpkt
import math
import os

HTTP_PREFIX = 'http://'
INTERVAL_SIZE = 100

TRACE_FILENAME = 'output.pcap'
START_END_FORMAT_STR = 'start_end_time_{0}'

def parse_file(root_dir, percent_bytes_to_ignore):
    for path, _, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            continue

        pcap_full_path = os.path.join(path, 'output.pcap')
        with open(pcap_full_path) as pcap_file:
            pcap_objects = dpkt.pcap.Reader(pcap_file)
            current_diff = -1
            bytes_received_per_interval = []
            page = extract_url(path)
            print 'page: ' + page
            start_end_filename = os.path.join(path, START_END_FORMAT_STR.format(page))
            total_bytes_filename = os.path.join(path, 'bytes_received.txt')
            exception_counter = 0
            if not os.path.exists(start_end_filename) or \
                not os.path.exists(total_bytes_filename):
                continue

            current_page_load_interval = get_page_load_interval(start_end_filename)
            current_page_bytes_interval = get_bytes_interval(total_bytes_filename, percent_bytes_to_ignore)
            current_output_filename = os.path.join(path, 'bandwidth.txt')
            current_output_file = open(current_output_filename, 'wb')
            start_ts = None # start_ts is inclusive
            end_ts = None # end_ts is exclusive.
            bytes_received = 0
            try:
                for ts, buf in pcap_objects:
                    ts = ts * 1000
                    # if ts > current_page_load_interval[1]:
                    #     # output to the file.
                    #     break

                    if not current_page_load_interval[0] <= ts <= current_page_load_interval[1]:
                        # The current timestamp is not in the page interval.
                        continue

                    eth = dpkt.ethernet.Ethernet(buf)
                    if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                        # Only use IP packets 
                        continue

                    ip = eth.data
                    try:
                        tcp = ip.data
                        if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                            # We only care about HTTP or HTTPS
                            continue

                        #print 'diff: ' + str(int(ts - start_ts)) + ' ts: ' + str(ts) + ' first_ts: ' + str(first_ts)
                        bytes_received += ip.len
                        if current_page_bytes_interval[0] <= bytes_received <= current_page_bytes_interval[1]:
                            if start_ts is None:
                                start_ts = ts
                            # Within the bytes interval we want to get the utilizations.
                            current_diff = int(ts - start_ts) / INTERVAL_SIZE # diff 
                            #print 'Current Diff: ' + str(current_diff)
                            while len(bytes_received_per_interval) < current_diff:
                                bytes_received_per_interval.append(0)
                            if len(bytes_received_per_interval) == current_diff:
                                # There isn't a bucket for this interval yet.
                                bytes_received_per_interval.append(0)
                            bytes_received_per_interval[int(current_diff)] += ip.len
                        if current_page_bytes_interval[1] < bytes_received or \
                            bytes_received == current_page_bytes_interval[1]: # Covers no bytes are ignored.
                            # Out of the bytes interval.
                            end_ts = ts
                            expected_slots = int(math.ceil(1.0 * (end_ts - start_ts) / INTERVAL_SIZE))
                            check_result(bytes_received_per_interval, expected_slots)
                            interval_timestamps = get_interval_timestamps(start_ts, expected_slots) # A list containing tuples indicating the start and end of an interval
                            measurement_interval = (start_ts, end_ts)
                            output_measurement_interval(page, measurement_interval, path)
                            output_to_file(bytes_received_per_interval, interval_timestamps, measurement_interval, current_output_file)
                            print 'expected_slots: {0} result len: {1} start_ts: {2:f} end_ts: {3:f}'.format(expected_slots, len(bytes_received_per_interval), start_ts, end_ts)
                            break
                    except Exception as e:
                        exception_counter += 1
                        print 'Exception: {0}'.format(e)
                        pass
            except dpkt.NeedData as e1:
                pass
            print '{0} done. Faulty packets: {1}'.format(page, exception_counter)

def extract_url(path):
    '''
    Extracts the url from the path.
    '''
    delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            delim_index = i
    return path[delim_index + 1:]

def get_interval_timestamps(start_ts, expected_slots):
    '''
    Get the interval timestamps.
    '''
    result = []
    start = start_ts
    end = start_ts + INTERVAL_SIZE
    for i in range(0, expected_slots):
        result.append((start, end))
        start = end
        end += INTERVAL_SIZE
    return result

def check_result(result, expected_num_slots):
    '''
    Checks whether the result has the expected number of slots. If not, append zeroes to the result list.
    '''
    slots_missing = expected_num_slots - len(result)
    for i in range(0, slots_missing):
        result.append(0.0)

def output_measurement_interval(page, measurement_interval, path):
    '''
    Outputs the measurement interval.
    '''
    with open(os.path.join(path, 'start_end_time_ignoring_bytes.txt'), 'wb') as output_file:
        output_file.write('{0} {1:f} {2:f}\n'.format(page, measurement_interval[0], measurement_interval[1]))

def output_to_file(bytes_received_per_interval, interval_timestamps, measurement_interval, output_file):
    counter = 0
    running_sum = 0
    for i in range(0, len(bytes_received_per_interval)):
        bytes_received = bytes_received_per_interval[i]  # 100ms per one slot
        running_sum += bytes_received
        utilization = convert_to_mbits(bytes_received) / 0.6 # each 100ms can handle 6mbps * 0.1(s/100ms) = 0.6 mbits
        # utilization = convert_to_mbits(bytes_received) # just the actual speed.
        line = '{0} {1} {2:f} {3:f}\n'.format((i * INTERVAL_SIZE), utilization, interval_timestamps[i][0], interval_timestamps[i][1])
        output_file.write(line)
        running_sum = 0

def convert_to_mbits(byte):
    return 1.0 * (byte * 8) / 1048576

def get_page_load_interval(page_load_interval_filename):
    with open(page_load_interval_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return int(line[1]), int(line[2])

def get_bytes_interval(total_bytes_filename, percent_bytes_to_ignore):
    '''
    Returns the bytes interval
    '''
    with open(total_bytes_filename, 'rb') as input_file:
        total_bytes = int(input_file.readline().strip())
        bytes_ignoring = int(round(0.01 * percent_bytes_to_ignore * total_bytes))
        return (bytes_ignoring, (total_bytes - bytes_ignoring))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--percent-bytes-to-ignore', type=int, default=0)
    args = parser.parse_args()
    parse_file(args.root_dir, args.percent_bytes_to_ignore)
