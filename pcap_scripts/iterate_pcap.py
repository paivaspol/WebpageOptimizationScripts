import argparse
import dpkt

def go_through_pcap(trace_filename):
    with open(trace_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        for ts, buf in pcap_objects:
            print str(ts)

if __name__ == '__main__':
    parser = argparse.ArgumentParser() 
    parser.add_argument('trace_filename') 
    args = parser.parse_args()
    go_through_pcap(args.trace_filename)

