from argparse import ArgumentParser
from collections import defaultdict

import common
import json
import os

FETCH_INCREASE_THRESHOLD = -1000

def Main():
    replay_fetch_times = GetFetchTimesFromNetworkFile(args.page_network_file)
    ha_fetch_times = GetFetchTimesFromDBQuery(args.page_request_info)
    for r in replay_fetch_times:
        if r not in ha_fetch_times:
            continue
        diff = ha_fetch_times[r] - replay_fetch_times[r]
        print('\t{0} {1} {2} {3}'.format(
            r, ha_fetch_times[r], replay_fetch_times[r], diff))


def GetReplayFetchTimes(root_dir):
    '''
    Returns a dictionary mapping from the pageurl to a dictionary of request
    fetch times.
    '''
    fetch_times = {}
    for d in os.listdir(root_dir):
        network_filename = os.path.join(root_dir, d, 'network_' + d)
        if not os.path.exists(network_filename):
            continue
        fetch_times[d] = GetFetchTimesFromNetworkFile(network_filename)
    return fetch_times


def GetFetchTimesFromNetworkFile(network_filename):
    '''
    Returns a dictionary mapping from the request url to fetch times measured
    from the difference between the timestamp when the fetch is complete and 
    when the request is sent.
    '''
    fetch_times = {}
    with open(network_filename, 'r') as input_file:
        request_started = {}
        request_id_to_url = {}
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                request_id = e['params']['requestId']
                url = e['params']['request']['url']
                ts = float(e['params']['timestamp'])
                request_started[request_id] = ts
                request_id_to_url[request_id] = url
            elif e['method'] == 'Network.loadingFinished':
                request_id = e['params']['requestId']
                ts = e['params']['timestamp']
                if request_id not in request_started:
                    continue
                # Convert to ms 
                url = request_id_to_url[request_id]
                fetch_time = int((ts - request_started[request_id]) * 1000)
                fetch_times[common.RemoveQuery(url)] = fetch_time
    return fetch_times


def GetFetchTimesFromHARequestInfo(request_info_filename):
    '''
    Parses the request info file from HTTP Archive and returns the fetch times
    of requests.

    Returns:
    A dictionary mapping from pageurl --> request URL --> fetch time
    '''
    fetch_times = defaultdict(lambda: defaultdict(dict))
    with open(request_info_filename, 'r') as input_file:
        for l in input_file:
            r = json.loads(l.strip())
            pageurl = common.escape_page(r['pageurl'])
            resource_url = r['url']
            payload = json.loads(r['payload'])
            fetch_time = payload['time']
            fetch_times[pageurl][resource_url] = fetch_time
    return fetch_times


def GetFetchTimesFromDBQuery(request_fetch_times_filename):
    '''
    Parses the output from the database and returns a dictionary mapping from
    the request URL to the fetch time.
    '''
    with open(request_fetch_times_filename, 'r') as input_file:
        retval = {}
        for i, l in enumerate(input_file):
            if i == 0:
                continue
            l = l.strip().split()
            retval[common.RemoveQuery(l[1])] = int(l[2])
        return retval


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_request_info')
    parser.add_argument('page_network_file')
    args = parser.parse_args()
    Main()
