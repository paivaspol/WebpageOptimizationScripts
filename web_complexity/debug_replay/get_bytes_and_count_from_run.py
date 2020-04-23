from argparse import ArgumentParser
from collections import defaultdict

import common
import json
import os

WEBCOMPLEXITY = 'webcomplexity.com'
ARCHIVE_ORG = 'archive.org'

def Main():
    pages_to_ignore = []
    for d in os.listdir(args.root_dir):
        if args.debug and args.debug not in d:
            continue
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        load_time = -1
        if args.up_to_onload:
            plt_filename = os.path.join(args.root_dir, d, 'start_end_time_' + d)
            if not os.path.exists(plt_filename):
                # print('here: ' + plt_filename)
                continue
            load_time = common.GetReplayPltMs(plt_filename)

        total_bytes, total_count = GetBytesAndCount(network_filename,
                load_time=load_time)
        if total_bytes == 0 or total_count <= 1:
            pages_to_ignore.append(d)
            continue
        print('{0} {1} {2}'.format(d, total_count, total_bytes))

    if args.output_broken_pages is not None:
        with open(args.output_broken_pages, 'w') as output_file:
            for p in pages_to_ignore:
                output_file.write(p + '\n')


def GetBytesAndCount(network_filename, load_time=-1):
    with open(network_filename, 'r') as input_file:
        req_ids = set()
        urls = []
        url_to_size = defaultdict(int)
        # only maps to the last URL in the redirection chain.
        req_id_to_url = {}
        total_bytes = 0
        first_ts_ms = -1
        sum_content_length = 0
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                # print(e)
                req_id = e['params']['requestId']
                url = e['params']['request']['url']
                timestamp_ms = e['params']['timestamp'] * 1000 # Convert to ms
                if first_ts_ms == -1:
                    first_ts_ms = timestamp_ms
                if WEBCOMPLEXITY in url or ARCHIVE_ORG in url or not url.startswith('http'):
                    continue

                # Cut at load time.
                if load_time != -1 and timestamp_ms - first_ts_ms > load_time:
                    continue

                if 'redirectResponse' in e['params']:
                    redirect_req_id = e['params']['requestId'] + '-redirect'
                    req_ids.add(redirect_req_id)
                    # Take care of the redirect URL
                    url = e['params']['redirectResponse']['url']
                    # urls.append(url)
                    if e['params']['redirectResponse']['fromDiskCache']:
                        continue
                    urls.append(url)
                    url_to_size[url] = e['params']['redirectResponse']['encodedDataLength']
                    if args.debug:
                        print('Added: ' + url)
                # req_ids.add(req_id)
                # urls.append(url)
            elif e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                url = e['params']['response']['url']
                if WEBCOMPLEXITY in url or ARCHIVE_ORG in url or not url.startswith('http'):
                    continue
                req_id_to_url[req_id] = url
                timestamp_ms = e['params']['timestamp'] * 1000 # Convert to ms

                if e['params']['response']['status'] != 200:
                    continue

                # Ignore resources from cache.
                if e['params']['response']['fromDiskCache']:
                    continue

                # Cut at load time.
                if load_time != -1 and timestamp_ms - first_ts_ms > load_time:
                    continue

                if req_id not in req_ids:
                    url = e['params']['response']['url']
                    urls.append(url)
                    if args.debug:
                        print('Added: ' + url)
                req_ids.add(req_id)
                url_to_size[url] += e['params']['response']['encodedDataLength']
                sum_content_length += common.GetContentLength(e['params']['response']['headers'])
            elif e['method'] == 'Network.requestServedFromCache':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    continue
                url = req_id_to_url[req_id]
                if url in urls:
                    urls.remove(url)
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    continue
                url = req_id_to_url[req_id]
                size = int(e['params']['encodedDataLength'])
                url_to_size[url] = size
                total_bytes += size
        if args.ignore_duplicates:
            total_bytes = sum([x[1] for x in url_to_size.items()])
            num_resources = len(url_to_size)
        else:
            num_resources = len(urls)
        return total_bytes, num_resources

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--output-broken-pages', default=None)
    parser.add_argument('--up-to-onload', default=False, action='store_true')
    parser.add_argument('--ignore-duplicates', default=False,
            action='store_true')
    parser.add_argument('--debug', default=None)
    args = parser.parse_args()
    Main()
