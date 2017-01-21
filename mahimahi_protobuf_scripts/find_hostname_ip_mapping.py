from argparse import ArgumentParser
from collections import defaultdict

import http_record_pb2

import os

def main(record_directory):
    files = os.listdir(record_directory)
    host_to_ip = dict()
    ip_to_hosts = defaultdict(set)
    for f in files:
        full_path = os.path.join(record_directory, f)
        host, ip = get_host_and_ip(full_path)
        host_to_ip[host] = ip
        ip_to_hosts[ip].add(host)

    for host, ip in host_to_ip.iteritems():
        print host + ' ' + ip
    
    for ip, hosts in ip_to_hosts.iteritems():
        if len(hosts) > 1:
            print ip + ' ' + str(hosts)

def get_host_and_ip(filename):
    hostname_to_ip = dict()
    with open(filename, 'rb') as input_file:
        file_content = input_file.read()
        request_response = http_record_pb2.RequestResponse()
        request_response.ParseFromString(file_content)
        first_line = request_response.request.first_line

        ip = request_response.ip

        splitted_first_line = first_line.split()
        for header_pair in request_response.request.header:
            if header_pair.key == 'Host':
                host = header_pair.value
        return host, ip

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('record_directory')
    args = parser.parse_args()
    main(args.record_directory)
