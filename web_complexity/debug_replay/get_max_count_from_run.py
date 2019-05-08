from argparse import ArgumentParser
from collections import defaultdict

import json
import os

def Main():
    pages_to_ignore = []
    page_reqs = defaultdict(list)
    for i in range(0, args.iterations):
        iter_dir = os.path.join(args.root_dir, str(i))
        for d in os.listdir(iter_dir):
            # if 'smbc-card.com' not in d:
            #     continue
            network_filename = os.path.join(iter_dir, d, 'network_' + d)
            total_count = GetBytesAndCount(network_filename)
            if total_count <= 1:
                pages_to_ignore.append(d)
                continue
            page_reqs[d].append(total_count)

    for p, reqs in page_reqs.items():
        print('{0} {1} {2}'.format(p, max(reqs), -1))


def GetBytesAndCount(network_filename):
    with open(network_filename, 'r') as input_file:
        req_ids = set()
        urls = []
        req_id_to_requests = {}
        total_bytes = 0
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
                req_ids.add(req_id)
                urls.append(url)
            elif e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    url = e['params']['response']['url']
                    urls.append(url)
                req_ids.add(req_id)
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                if req_id not in req_ids:
                    if req_id in req_id_to_requests:
                        print('Missing: {0} {1}'.format(req_id,
                            req_id_to_requests[req_id]))
                    continue
                size = int(e['params']['encodedDataLength'])
                total_bytes += size
        # print(req_ids)
        return len(urls)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('iterations', type=int)
    args = parser.parse_args()
    Main()
