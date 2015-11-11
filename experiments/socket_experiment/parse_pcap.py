import dpkt

from argparse import ArgumentParser

def main(pcap_filename, start_time, end_time):
    with open(pcap_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        acks_received = set()
        first_ts = None
        for ts, buf in pcap_objects:
            if start_time <= ts <= end_time:
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    # Only use IP packets 
                    continue
                if first_ts is None:
                    first_ts = ts
                ip = eth.data
                # Check that the src and dst IP are the ones that we want.
                tcp = ip.data
                if (tcp.flags | dpkt.tcp.TH_ACK) != 0:
                    # print str(ts - first_ts)
                    if tcp.ack not in acks_received:
                        print str(ts)
                        acks_received.add(tcp.ack)
            elif ts > end_time:
                break
        print 'Number of ACKs: {0}'.format(len(acks_received))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_file')
    parser.add_argument('start_time', type=float)
    parser.add_argument('end_time', type=float)
    args = parser.parse_args()
    main(args.pcap_file, args.start_time, args.end_time)
    

