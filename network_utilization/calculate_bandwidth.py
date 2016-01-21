from argparse import ArgumentParser

import common_module
import dpkt
import math

def iterate_pcap(pcap_filename, start_time, end_time):
    with open(pcap_filename, 'rb') as input_file:
        pcap_objects = dpkt.pcap.Reader(input_file)
        bytes_received = 0
        bytes_slots, last_slot_interval = generate_expected_slots(start_time, end_time)
        for ts, buf in pcap_objects:
            if not start_time <= ts <= end_time:
                continue

            eth = dpkt.ethernet.Ethernet(buf)
            if eth.type != dpkt.ethernet.ETH_TYPE_IP:
                # Only use IP packets 
                continue

            ip = eth.data
            tcp = ip.data
            if int(ip.p) != int(dpkt.ip.IP_PROTO_TCP) or not common_module.check_web_port(True, tcp.sport):
                # We only care about HTTP or HTTPS
                continue
            bytes_received += ip.len
            bytes_slots_index = int((ts - start_time) * 10)
            bytes_slots[bytes_slots_index] += ip.len
        bandwidth = common_module.convert_to_mbits(bytes_received) / (end_time - start_time)
    print 'bandwidth: ' + str(bandwidth) + ' utilization: ' + str(bandwidth / 6.0)
    print 'utilization: ' + str(generate_utilizations(bytes_slots, last_slot_interval))

def generate_expected_slots(start_time, end_time):
    load_time = (end_time - start_time) * 1000
    last_slot_interval = load_time % 100
    expected_slots = int(math.ceil(load_time / 100))
    result = []
    for i in range(0, expected_slots):
        result.append(0)
    return result, last_slot_interval

def generate_utilizations(bandwidth_list, last_slot_interval):
    utilizations = []
    for i in range(0, len(bandwidth_list)):
        bandwidth = common_module.convert_to_mbits(bandwidth_list[i]) * 10
        expected_utilization = 6.0 / (1000 / 100)
        if i == len(bandwidth_list) - 1:
            expected_utilization = 6.0 / (1000 / last_slot_interval)
        utilizations.append(bandwidth / 6.0)
    return utilizations

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pcap_filename')
    parser.add_argument('start_time', type=float)
    parser.add_argument('end_time', type=float)
    args = parser.parse_args()
    print 'load time: ' + str((args.end_time - args.start_time) * 1000)
    iterate_pcap(args.pcap_filename, args.start_time, args.end_time)

