from argparse import ArgumentParser

import dpkt

THRESHOLD = 15.0

def find_utilization_time(pcap_filename, start_interval, end_interval):
    cumulative_idle_time = 0.0
    total_time = 0.0
    with open(pcap_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        prev_ts = None
        cur_ts = None
        initial_ts = None
        for ts, buf in pcap_objects:
            ts = ts * 1000 # Convert to ms precision

            if not start_interval <= ts:
                continue
            elif ts > end_interval:
                break

            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                # Only use IP packets.
                continue
            
            ip = eth.data
            tcp = ip.data
            if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                # We only care about HTTP or HTTPS
                continue
            
            if cur_ts is None:
                # Set the initial cur_ts
                cur_ts = ts
                initial_ts = ts
                continue
    
            # Update the timestamps
            prev_ts = cur_ts
            cur_ts = ts
            idle_time = cur_ts - prev_ts
            if idle_time > THRESHOLD:
                cumulative_idle_time += idle_time
        total_time = cur_ts - initial_ts
    print 'total: {0} idle: {1} fraction: {2}'.format(total_time, cumulative_idle_time, (1.0 * cumulative_idle_time / total_time))

def output_to_file(total_time, cumulative_idle_time, path):
    output_filename = 'time_spent_breakdown.txt'
    with open(os.path.join(path, output_filename), 'wb') as output_file:
        output_file.write('{0:f} {1:f} {2}\n'.format(total_time, cumulative_idle_time, (1.0 * cumulative_idle_time / total_time)))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('start_interval', type=float)
    parser.add_argument('end_interval', type=float)
    args = parser.parse_args()
    find_utilization_time(args.pcap_filename, args.start_interval, args.end_interval)
