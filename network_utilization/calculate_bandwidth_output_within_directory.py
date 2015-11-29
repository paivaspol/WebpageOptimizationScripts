import argparse
import dpkt
import os

HTTP_PREFIX = 'http://'
INTERVAL_SIZE = 100

TRACE_FILENAME = 'output.pcap'
START_END_FORMAT_STR = 'start_end_time_{0}'

def parse_file(root_dir):
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
            if not os.path.exists(start_end_filename):
                continue

            current_page_load_interval = get_page_load_interval(start_end_filename)
            current_output_filename = os.path.join(path, 'bandwidth.txt')
            current_output_file = open(current_output_filename, 'wb')
            first_ts = current_page_load_interval[0]
            for ts, buf in pcap_objects:
                ts = ts * 1000
                if ts > current_page_load_interval[1]:
                    # output to the file.
                    print 'result len: ' + str(len(bytes_received_per_interval))
                    output_to_file(bytes_received_per_interval, current_output_file)
                    break

                if not current_page_load_interval[0] <= ts <= current_page_load_interval[1]:
                    # The current timestamp is not in the page interval.
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

                #print 'diff: ' + str(int(ts - first_ts)) + ' ts: ' + str(ts) + ' first_ts: ' + str(first_ts)
                current_diff = int(ts - first_ts) / INTERVAL_SIZE # diff 
                #print 'Current Diff: ' + str(current_diff)
                while len(bytes_received_per_interval) < current_diff:
                    bytes_received_per_interval.append(0)
                if len(bytes_received_per_interval) == current_diff:
                    # There isn't a bucket for this interval yet.
                    bytes_received_per_interval.append(0)
                bytes_received_per_interval[int(current_diff)] += ip.len
    print 'Done.'

def extract_url(path):
    delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            delim_index = i
    return path[delim_index + 1:]

def output_to_file(bytes_received_per_interval, output_file):
    counter = 0
    running_sum = 0
    for i in range(0, len(bytes_received_per_interval)):
        bytes_received = bytes_received_per_interval[i]  # 100ms per one slot
        running_sum += bytes_received
        utilization = convert_to_mbits(bytes_received) / 0.6 # each 100ms can handle 6mbps * 0.1(s/100ms) = 0.6 mbits
        # utilization = convert_to_mbits(bytes_received) # just the actual speed.
        line = str(i * INTERVAL_SIZE) + ' ' + str(utilization)
        output_file.write(line + '\n')
        running_sum = 0

def convert_to_mbits(byte):
    return 1.0 * (byte * 8) / 1048576

def get_page_load_interval(page_load_interval_filename):
    with open(page_load_interval_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return int(line[1]), int(line[2])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    parse_file(args.root_dir)
