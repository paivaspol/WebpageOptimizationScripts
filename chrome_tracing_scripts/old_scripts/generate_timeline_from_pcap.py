from argparse import ArgumentParser

import dpkt

def iterate_pcap_file(pcap_filename, start_end_time):
    with open(pcap_filename, 'rb') as pcap_file:
        pcap_objects = dpkt.pcap.Reader(pcap_file)
        try:
            for ts, buf in pcap_objects:
                if not start_end_time[1][0] <= ts * 1000 <= start_end_time[1][1]:
                    # Ignore ones that are not in range
                    continue
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                    continue
                ip = eth.data
                tcp = ip.data
                if tcp.sport == 44300:
                    time_diff = ((ts * 1000) - start_end_time[1][0]) / 1000
                    line = '{0} {1} {2}'.format(1, 'pcap', time_diff)
                    print line
        except dpkt.NeedData as e:
            pass

def get_start_end_time(start_end_time_filename):
    with open(start_end_time_filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        return (line[0], (int(line[1]), int(line[2])))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('start_end_time_filename')
    args = parser.parse_args()
    start_end_time = get_start_end_time(args.start_end_time_filename)
    iterate_pcap_file(args.pcap_filename, start_end_time)
