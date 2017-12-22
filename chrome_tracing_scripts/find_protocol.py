from argparse import ArgumentParser
from urlparse import urlparse

import constants
import json
import os

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for p in os.listdir(root_dir):
        network_filename = os.path.join(root_dir, p, 'network_' + p)
        output_filename = os.path.join(output_dir, p)
        if not os.path.exists(network_filename):
            continue
        domain_proto_dict = find_protocol_per_domain(network_filename)
        output_to_file(domain_proto_dict, output_filename)

def output_to_file(domain_proto_dict, output_filename):
    with open(output_filename, 'wb') as output_file:
        for domain, proto in domain_proto_dict.iteritems():
            output_file.write('{0} {1}\n'.format(domain, proto))

def find_protocol_per_domain(network_filename):
    domain_protocol_dict = {}
    with open(network_filename, 'rb') as input_file:
        for l in input_file:
            network_event = json.loads(l.strip())
            if network_event[constants.METHOD] == constants.NET_RESPONSE_RECEIVED:
                url = network_event[constants.PARAMS][constants.RESPONSE][constants.URL]
                domain = urlparse(url).netloc
                protocol = network_event[constants.PARAMS][constants.RESPONSE][constants.PROTOCOL]
                if domain not in domain_protocol_dict:
                    domain_protocol_dict[domain] = protocol
    return domain_protocol_dict

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
