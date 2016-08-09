#!/usr/bin/env python

import dpkt
import numpy
import re
import socket
import sys

ETH_TYPE_IPV4=2048
PROTO_TCP=6
RAW_IP = False

def syn_syn_ack_times(pcap_file):
    """Reads in pcap and returns a dict mapping server IP to
       list of SYN-ACK times (in milliseconds)."""

    # dictionary mapping server IP to median SYN, SYN-ACK time
    rtt_dict = {}

    f = open(pcap_file)
    pcap = dpkt.pcap.Reader(f)

    # dictionary mapping server IP to a list of SYN, SYN-ACK times
    rtt_list_dict = {}

    # dictionary mapping (server IP, client port) to SYN time
    syn_times = {}

    try:
        for ts, buf in pcap:
            if RAW_IP:
                # RAW IP
                ip = dpkt.ip.IP(buf)
            else:
                # ethernet
                eth = dpkt.ethernet.Ethernet(buf)

                # get IPv4 header
                if eth.type != ETH_TYPE_IPV4:
                    continue
                ip = eth.data

            # only look at TCP packets
            if ip.p != PROTO_TCP:
                continue

            tcp = ip.data

            if (((tcp.flags & dpkt.tcp.TH_SYN) != 0) and
                ((tcp.flags & dpkt.tcp.TH_ACK) == 0)):
                # SYN without ACK, client -> server
                server_ip = socket.inet_ntoa(ip.dst)
                client_port = tcp.sport
                syn_times[(server_ip, client_port)] = float(ts)
            elif (((tcp.flags & dpkt.tcp.TH_SYN) != 0) and
                  ((tcp.flags & dpkt.tcp.TH_ACK) != 0)):
                # SYN/ACK, server -> client
                server_ip = socket.inet_ntoa(ip.src)
                client_port = tcp.dport

                if (server_ip, client_port) not in syn_times:
                    # this is likely a retransmission of a SYN/ACK packet
                    continue

                # rtt_sample is current time minus SYN time
                prev_time = syn_times[(server_ip, client_port)]
                del syn_times[(server_ip, client_port)]
                rtt_sample = float(ts) - prev_time
                # convert RTT sample to milliseconds
                rtt_sample = round(rtt_sample * 1000, 3)

                sample_list = rtt_list_dict.get(server_ip, [])
                sample_list.append(rtt_sample)
                rtt_list_dict[server_ip] = sample_list

    except dpkt.dpkt.NeedData:
        print "WARNING: NeedData raised"

    return rtt_list_dict

def main():
    args = sys.argv

    if len(args) < 2:
        print 'Usage: python %s pcap_file' % str(args[0])
        exit()

    pcap_file = args[1]

    print syn_syn_ack_times(pcap_file)

if __name__ == "__main__":
    main()
