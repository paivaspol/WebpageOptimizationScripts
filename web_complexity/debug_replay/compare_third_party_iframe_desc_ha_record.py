from argparse import ArgumentParser
from collections import defaultdict

import common
import json
import os

def Main():
    ha_page_referer_bytes, ha_page_referer_count = GetHAPageRefererBytes(args.requests_filename)
    recorded_bytes, recorded_count = GetRecordedBytes(args.recorded_dir)

    for url in recorded_bytes:
        if url not in ha_page_referer_bytes:
            # Skip
            continue

        for iframe in recorded_bytes[url]:
            if iframe not in ha_page_referer_bytes[url]:
                # Skip
                continue

            ha_bytes = ha_page_referer_bytes[url][iframe]
            ha_count = ha_page_referer_count[url][iframe]
            record_bytes = recorded_bytes[url][iframe]
            record_count = recorded_count[url][iframe]

            print('{0} {1} {2} {3} {4} {5}'.format(url, iframe, ha_count,
                record_count, ha_bytes, record_bytes))


def GetRecordedBytes(recorded_dir):
    '''Returns a tuple of double map from the pageurl --> referer --> bytes and
    double map from pageurl --> referer --> count.'''
    iframe_desc_bytes = defaultdict(dict)
    iframe_desc_count = defaultdict(dict)

    for d in os.listdir(recorded_dir):
        hash_to_url_filename = os.path.join(recorded_dir, d, 'hash_to_url')
        hash_to_urls = GetHashToUrl(hash_to_url_filename)

        # iterate each iframe under the recording dir.
        for h, url in hash_to_urls.items():
            network_filename = os.path.join(recorded_dir, d, 'devtools_logs',
                    '0', h, 'network_' + str(h))
            resp_count, total_bytes = ProcessNetworkFile(network_filename)
            iframe_desc_bytes[d][url] = total_bytes
            iframe_desc_count[d][url] = resp_count
    return (iframe_desc_bytes, iframe_desc_count)


def ProcessNetworkFile(network_filename):
    '''Processes the network file and returns a tuple of response count and total bytes.'''
    response_count = 0
    total_bytes = 0
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.responseReceived':
                response_count += 1
            elif e['method'] == 'Network.loadingFinished':
                total_bytes += e['params']['encodedDataLength']
    return (response_count, total_bytes)


def GetHashToUrl(hash_to_url_filename):
    with open(hash_to_url_filename, 'r') as input_file:
        return json.load(input_file)


def GetHAPageRefererBytes(ha_requests_filename):
    '''Returns a tuple of double map from the pageurl --> referer --> bytes and
    double map from pageurl --> referer --> count.'''
    with open(args.requests_filename, 'r') as input_file:
        iframe_desc_bytes = defaultdict(lambda: defaultdict(int))
        iframe_desc_count = defaultdict(lambda: defaultdict(int))
        for l in input_file:
            e = json.loads(l.strip())
            pageurl = e['page']
            entry = json.loads(e['payload'])
            referer = common.ExtractRefererFromHAEntry(entry)
            if referer is None or referer == pageurl or 'css' in referer:
                # Ignore anything that is not the main HTML.
                continue
            iframe_desc_bytes[common.escape_page(pageurl)][referer] += entry['_bytesIn']
            iframe_desc_count[common.escape_page(pageurl)][referer] += 1
        return (iframe_desc_bytes, iframe_desc_count)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    parser.add_argument('recorded_dir')
    args = parser.parse_args()
    Main()
