from argparse import ArgumentParser
from collections import defaultdict

import json
import os

def Main():
    # mime_types = set()
    # with open(args.requests_filename, 'r') as input_file:
    #     for i, l in enumerate(input_file):
    #         entry = json.loads(l.strip())
    #         payload = json.loads(entry['payload'])
    #         mime_type = payload['response']['content']['mimeType'].lower()
    #         mime_types.add(mime_type)
    # mime_types = list(mime_types)
    # mime_types.sort()
    # print('\n'.join(mime_types))
    print(json.dumps(GetMimeMapping(args.experiment_dir)))

def GetMimeMapping(experiment_dir):
    mime_to_resource_mapping = defaultdict(lambda: defaultdict(int))
    for d in os.listdir(experiment_dir):
        network_filename = os.path.join(experiment_dir, d, 'network_' + d)
        with open(network_filename, 'r') as input_file:
            for l in input_file:
                event = json.loads(l.strip())
                if event['method'] != 'Network.responseReceived':
                    continue
                mime_type = event['params']['response']['mimeType'].lower()
                resource_type = event['params']['type']
                mime_to_resource_mapping[mime_type][resource_type] += 1
    retval = {}
    for mime, type_count in mime_to_resource_mapping.items():
        sorted_type_count = sorted(type_count.items(), key=lambda x: x[1],
                reverse=True)
        retval[mime] = sorted_type_count[0][0]
    return retval

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('experiment_dir')
    args = parser.parse_args()
    Main()
