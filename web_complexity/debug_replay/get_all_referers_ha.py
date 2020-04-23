from argparse import ArgumentParser
from collections import defaultdict

import common
import json
import os

def Main():
    requests_filename = os.path.join(args.splitted_data_dir, args.page,
        'requests.json')
    resp_bodies_filename = os.path.join(args.splitted_data_dir, args.page,
        'response_bodies.json')
    has_resp = set()
    with open(resp_bodies_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            has_resp.add(e['url'])

    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            entry = json.loads(e['payload'])
            referer = common.ExtractRefererFromHAEntry(entry)
            initiator = entry['_initiator'] if '_initiator' in entry else None
            has_resp_str = 'HAS_RESP' if e['url'] in has_resp else 'FETCHED'
            print('{0} {1} {2} {3}'.format(e['url'], referer, initiator,
                has_resp_str))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('splitted_data_dir')
    parser.add_argument('page')
    args = parser.parse_args()
    Main()
