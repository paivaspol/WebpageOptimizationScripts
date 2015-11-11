import argparse
import dpkt

def go_through_pcap(trace_filename, start_time):
    with open(trace_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        for ts, buf in pcap_objects:
            # print str(ts)
            ts = ts * 1000
            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                continue

            ip = eth.data
            tcp = ip.data
            if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or (tcp.sport != 443 and tcp.sport != 80):
                # We only care about HTTP or HTTPS
                continue
            try:
                if len(tcp.data) > 0:
                    if str(tcp.data[9:12].decode('utf-8')) == '200':
                        relative_time = ts - start_time
                        print '0.55 {0} {1}'.format(relative_time, relative_time + 0.5)
            except (dpkt.dpkt.UnpackError, UnicodeDecodeError, UnicodeEncodeError, IndexError) as e:
                pass

def parse_timestamp_file(timestamp_filename):
    with open(timestamp_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        start_time = int(line[1])
    return start_time
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('trace_filename') 
    parser.add_argument('timestamp_filename')
    args = parser.parse_args()
    start_time = parse_timestamp_file(args.timestamp_filename)
    go_through_pcap(args.trace_filename, start_time)

