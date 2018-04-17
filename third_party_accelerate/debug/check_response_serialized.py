'''
This script checks if the responses are serialized by checking that there are 
no two responses that have overlaping response receiving time.
'''
from argparse import ArgumentParser
from collections import defaultdict

import json

def main(network_filename):
    response_times, response_order = construct_response_times(network_filename)
    cur_response_time = None
    cur_response = None
    for r in response_order:
        r_response_time = response_times[r]
        if cur_response_time is None:
            cur_response_time = r_response_time
            cur_response = r
            continue
        if cur_response_time[1] >= r_response_time[0]:
            # The start time of a subsequent response is before the end time of a previous response.
            print 'Response overlapped... {0} and {1}'.format(cur_response, r)
            break
        cur_response_time = r_response_time
        cur_response = r
    print 'No overlap'

def construct_response_times(network_filename):
    '''
    Constructs a dictionary mapping to a list of two elements: (first_byte_time, last_byte_time)
    '''
    response_times = defaultdict(list)
    response_order = []
    with open(network_filename, 'rb') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.responseReceived' or e['method'] == 'Network.loadingFinished':
                request_id = e['params']['requestId']
                if e['method'] == 'Network.responseReceived':
                    response_order.append(request_id)
                ts = e['params']['timestamp']
                response_times[request_id].append(ts)
    return response_times, response_order


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    main(args.network_filename)
