from argparse import ArgumentParser
from collections import defaultdict

import common
import json

HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'
def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


def Main():
    all_reqs = []
    with open(args.json_file, 'r') as input_file:
        for l in input_file:
            all_reqs.append(json.loads(l))

    req_size_mapping = defaultdict(int) # Maps from pageurl --> size
    req_count_mapping = defaultdict(int)

    onload_ts_ms = None
    if args.up_to_onload:
        onload_ts_ms = common.GetLoadTimesTsMs(args.up_to_onload)

    for req in all_reqs:
        page = escape_page(req['page'])
        req_url = req['url']
        payload = json.loads(req['payload'])

        # if payload['_id'].startswith('99999'):
        #     # This is a service worker request. Ignore.
        #     continue

        start_ts_epoch_ms = common.GetTimestampSinceEpochMs(payload['startedDateTime'])
        load_time_ms = payload['time'] if 'time' in payload else -1
        if onload_ts_ms is not None and (load_time_ms == -1 or page not in onload_ts_ms or
                start_ts_epoch_ms + load_time_ms > onload_ts_ms[page]):
            # request after onload. ignore.
            continue

        # Find the response size:
        resp_size = payload['response']['content']['size']
        req_size_mapping[page] += resp_size
        req_count_mapping[page] += 1

    sorted_mapping = sorted(req_size_mapping.items(), key=lambda x: x[1])
    for pageurl, size in sorted_mapping:
        count = req_count_mapping[pageurl]
        print('{0} {1} {2}'.format(pageurl, count, size))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('json_file')
    parser.add_argument('--up-to-onload', default=None)
    args = parser.parse_args()
    Main()
