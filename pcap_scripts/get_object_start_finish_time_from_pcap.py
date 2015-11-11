import argparse
import dpkt

def go_through_pcap(trace_filename, timestamp_tuple):
    object_finish_times = []
    with open(trace_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        for ts, buf in pcap_objects:
            if ts > timestamp_tuple[1]:
                break
            elif ts < timestamp_tuple[0]:
                continue

            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                continue

            ip = eth.data
            tcp = ip.data
            if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP):
                continue
            
            try:
                if tcp.dport == 80:
                    #print tcp.data
                    http = dpkt.http.Request(tcp.data)
                    # print 'sport: {0}, dport: {1}'.format(tcp.sport, tcp.dport)
                    # print 'Method: {0}, URI: {1}'.format(http.method, http.uri)
                elif tcp.sport == 80:
                    http = dpkt.http.Response(tcp.data)
                    # print 'sport: {0}, dport: {1}'.format(tcp.sport, tcp.dport)
                    # print 'URI: {0}'.format(http.uri)
                    print len(http)
                    object_finish_times.append((http.uri, ts))
                    print str(object_finish_times)
            except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError) as e:
                pass
    
    for finish_time in object_finish_times:
        print '{0} {1}'.format(finish_time[0], finish_time[1])
            
def parse_timestamp_file(timestamp_filename):
    with open(timestamp_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return (int(line[1]) / 1000, int(line[2]) / 1000)

if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('trace_filename') 
    parser.add_argument('timestamp_filename')
    args = parser.parse_args()
    timestamps = parse_timestamp_file(args.timestamp_filename)
    go_through_pcap(args.trace_filename, timestamps)

