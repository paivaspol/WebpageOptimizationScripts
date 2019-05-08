from argparse import ArgumentParser
from collections import defaultdict
from multiprocessing import Pool

import common
import json
import os

def Main():
    results = []
    pool = Pool()
    for d in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        result = pool.apply_async(GetIframeDescForPage, args=(network_filename, ))
        results.append((d, result))
    pool.close()
    pool.join()

    for pageurl, r in results:
        first_party, third_party = r.get()
        third_party_desc = sum([ len(v) for _, v in third_party.items() ])
        print('{0} {1}'.format(pageurl, third_party_desc))


def GetIframeDescForPage(network_filename):
    '''Wrapper for multiprocessing.'''
    requests, main_frame_id = GetRequestsSortOnTime(network_filename)
    first_party_resources, third_party_breakdown = common.GetFrameBreakdown(requests, main_frame_id)
    return (first_party_resources, third_party_breakdown)


def GetRequestsSortOnTime(network_filename):
    requests_ts = []
    main_frame_id = None
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                frame_id = e['params']['frameId'] if 'frameId' in e['params'] else '-1'
                started_time_ms = e['params']['timestamp']
                requests_ts.append((url, started_time_ms, frame_id))

                # Assume that the first request corresponds to the main frame.
                if main_frame_id is None:
                    main_frame_id = frame_id
    requests_ts.sort(key=lambda x: (x[2], x[1]))
    return (requests_ts, main_frame_id)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
