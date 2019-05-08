from argparse import ArgumentParser

import common
import json
import os

def Main():
    pages_to_ignore = []
    for d in os.listdir(args.root_dir):
        # if 'sanook.com' not in d:
        #     continue
        network_filename = os.path.join(args.root_dir, d, 'network_' + d)
        load_time = -1
        if args.up_to_onload:
            plt_filename = os.path.join(args.root_dir, d, 'start_end_time_' + d)
            if not os.path.exists(plt_filename):
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
        req_id_to_requests = {}
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
                if url.startswith('data:'):
                    continue

                # Cut at load time.
                if load_time != -1 and timestamp_ms - first_ts_ms > load_time:
                    continue

                if 'redirectResponse' in e['params']:
                    redirect_req_id = e['params']['requestId'] + '-redirect'
                    req_ids.add(redirect_req_id)
                # req_ids.add(req_id)
                # urls.append(url)
            elif e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                timestamp_ms = e['params']['timestamp'] * 1000 # Convert to ms

                # Cut at load time.
                if load_time != -1 and timestamp_ms - first_ts_ms > load_time:
                    continue

                if req_id not in req_ids:
                    url = e['params']['response']['url']
                    urls.append(url)
                req_ids.add(req_id)

                sum_content_length += GetContentLength(e['params']['response']['headers'])
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    if req_id in req_id_to_requests:
                        print('Missing: {0} {1}'.format(req_id,
                            req_id_to_requests[req_id]))
                    continue
                size = int(e['params']['encodedDataLength'])
                total_bytes += size
        # print('Total bytes: {0} total content-length: {1}'.format(total_bytes,
        #    sum_content_length))
        # print(req_ids)
        # for u in urls:
        #     print(u)
        return total_bytes, len(urls)


def GetContentLength(headers):
    for k, v in headers.items():
        if k.lower() == 'content-length':
            return int(v)
    return -1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--output-broken-pages', default=None)
    parser.add_argument('--up-to-onload', default=False, action='store_true')
    args = parser.parse_args()
    Main()
