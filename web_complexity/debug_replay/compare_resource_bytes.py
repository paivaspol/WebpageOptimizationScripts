from argparse import ArgumentParser
from collections import defaultdict
from urlmatcher import RoughUrlMatcher

import common
import json

WEBCOMPLEXITY = 'webcomplexity.com'

def Main():
    ha_bytes, total_ha_bytes = GetHABytes(args.httparchive_requests_filename,
            args.httparchive_pages_filename)
    ha_urls = [ u for u in ha_bytes.keys() ]
    replay_bytes, _ = GetReplayBytes(args.replay_network_filename)
    print(len(replay_bytes))
    running_diffs = 0
    urlmatcher = RoughUrlMatcher()
    replay_dict_bytes = 0
    no_match_bytes = 0
    for url, size in replay_bytes.items():
        matched_url, _ = urlmatcher.Match(url, ha_urls, urlmatcher.SIFT4)
        print(matched_url)
        if url not in ha_bytes:
            print('\t[NO MATCH] {0}: {1}'.format(url, size))
            replay_dict_bytes += size
            no_match_bytes += size
            continue
        diff = ha_bytes[url] - size
        running_diffs += diff
        replay_dict_bytes += size
        print('{0} {1} {2} {3}'.format(url, ha_bytes[url], size, diff))
    print('Replay dict bytes: ' + str(replay_dict_bytes))
    print('Total diffs: ' + str(running_diffs))
    print('HA Bytes: ' + str(total_ha_bytes))
    print('No Match bytes: ' + str(no_match_bytes))


def GetReplayBytes(network_filename):
    with open(network_filename, 'r') as input_file:
        req_ids = set()
        urls = []
        req_id_to_requests = {}
        req_id_to_url = {}
        total_bytes = 0
        url_to_size = {}
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                # print(e)
                req_id = e['params']['requestId']
                url = e['params']['request']['url']
                if url.startswith('data:'):
                    continue

                if 'redirectResponse' in e['params']:
                    redirect_req_id = e['params']['requestId'] + '-redirect'
                    req_ids.add(redirect_req_id)
                # req_ids.add(req_id)
                # urls.append(url)
                req_id_to_url[req_id] = url
            elif e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                url = e['params']['response']['url']
                if WEBCOMPLEXITY in url:
                    continue

                if req_id not in req_ids:
                    url = e['params']['response']['url']
                    if url.startswith('data:'):
                        continue
                    urls.append(url)
                    req_id_to_url[req_id] = url
                req_ids.add(req_id)
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    continue
                url = req_id_to_url[req_id]
                size = int(e['params']['encodedDataLength'])
                if url in url_to_size:
                    print('\t[REPLAY DUP] ' + url + ' size:' + str(size))
                url_to_size[url] = size
                total_bytes += size
        print('total_replay_bytes: ' + str(total_bytes))
        return url_to_size, len(urls)


def GetHABytes(ha_requests_filename, ha_pages_filename):
    '''Returns a dict mapping from request URL --> bytes.'''
    req_size_mapping = defaultdict(int) # Maps from request url --> size
    onload_ts_ms = common.GetLoadTimesTsMs(ha_pages_filename)
    total_ha_bytes = 0
    with open(ha_requests_filename, 'r') as input_file:
        for l in input_file:
            req = json.loads(l.strip())
            page = common.escape_page(req['page'])
            req_url = req['url']
            payload = json.loads(req['payload'])

            start_ts_epoch_ms = common.GetTimestampSinceEpochMs(payload['startedDateTime'])
            load_time_ms = payload['time'] if 'time' in payload else -1
            if load_time_ms == -1 or page not in onload_ts_ms or \
                    start_ts_epoch_ms + load_time_ms > onload_ts_ms[page]:
                # request after onload. ignore.
                print('Igonring: {0}'.format(req_url))
                continue

            # Find the response size:
            resp_size = payload['response']['content']['size']
            if req_url in req_size_mapping:
                print('\t[HA DUP] {0}: {1}'.format(req_url, resp_size))
            req_size_mapping[req_url] += resp_size
            total_ha_bytes += resp_size
    return req_size_mapping, total_ha_bytes

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('httparchive_requests_filename')
    parser.add_argument('httparchive_pages_filename')
    parser.add_argument('replay_network_filename')
    args = parser.parse_args()
    Main()
