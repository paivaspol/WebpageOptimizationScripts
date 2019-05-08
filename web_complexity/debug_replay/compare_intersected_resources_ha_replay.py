'''
We want to plot the distribution of difference between intersected resources.
We want to see if the variance in bytes seen in the page loads is because of the
difference in binary resource sizes.

Binary resources are fetched individually and they may changed / generated on
the fly, so we want to see if this is the reason why we are seeing the
variation.
'''
from argparse import ArgumentParser
from collections import defaultdict

import common
import json
import os

RESOURCE_TYPES_TO_CHECK = { 'Image', 'Font' }

def GetHABytes(ha_filename):
    '''
    Returns a mapping from URL to size.

    This assumes that the `ha_filename` contains JSON object in each line and
    they are delimited by newlines.
    '''
    bytes_dict = defaultdict(dict)
    with open(ha_filename, 'r') as input_file:
        for l in input_file:
            resource = json.loads(l.strip())
            page = common.escape_page(resource['page'])
            url = resource['url']
            if not url.startswith('http'):
                # ignore non-http urls
                continue

            payload = json.loads(resource['payload'])
            try:
                bytes_fetched = int(payload['response']['content']['size'])
                bytes_dict[page][url] = bytes_fetched
            except Exception as e:
                pass
    return bytes_dict


def GetReplayBytes(network_filename):
    '''Returns a set of unique URLs seen in the network file.'''
    urls = set()
    requested = set()
    size_map = {}
    resource_types = {}
    req_id_to_url = {}
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                # print(e)
                req_id = e['params']['requestId']
                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue

                requested.add(url)
                req_id_to_url[req_id] = url
                resource_types[url] = e['params']['type']
            elif e['method'] == 'Network.responseReceived':
                url = e['params']['response']['url']
                if e['params']['response']['status'] == 200 and url in requested:
                    # print(e)
                    urls.add(url)
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                if req_id not in req_id_to_url:
                    continue
                url = req_id_to_url[req_id]
                size = e['params']['encodedDataLength']
                size_map[url] = int(size)
    return urls, size_map, resource_types


def GetBytesDiffForPage(ha_bytes, replay_file, output_filename):
    '''Finds the bytes diff for each of the page. The diff is "replay - HA".'''
    urls, replay_bytes, resource_types = GetReplayBytes(replay_file)
    total_ha_urls_bytes = 0
    total_replay_urls_bytes = 0
    with open(output_filename, 'w') as output_file:
        for url, replay_url_bytes in replay_bytes.items():
            if url not in ha_bytes:
                continue

            resource_type = resource_types[url]
            # if resource_type not in RESOURCE_TYPES_TO_CHECK:
            #     continue

            ha_url_bytes = ha_bytes[url]
            total_ha_urls_bytes += ha_url_bytes
            total_replay_urls_bytes += replay_url_bytes
            output_file.write('{0} {1} {2}\n'.format(
                url, ha_url_bytes, replay_url_bytes))
    return total_ha_urls_bytes, total_replay_urls_bytes


def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    ha_bytes = GetHABytes(args.ha_file)
    for d in os.listdir(args.replay_root_dir):
        replay_filename = os.path.join(args.replay_root_dir, d, 'network_' + d)
        output_filename = os.path.join(args.output_dir, d)
        page_ha_urls_bytes, page_replay_urls_bytes = GetBytesDiffForPage(
                ha_bytes[d], replay_filename, output_filename)
        diff = page_replay_urls_bytes - page_ha_urls_bytes
        if page_replay_urls_bytes <= 136:
            # 136 because it is the default 404 size.
            continue

        print('{0} {1} {2} {3}'.format(d, page_ha_urls_bytes,
            page_replay_urls_bytes, diff))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('ha_file')
    parser.add_argument('replay_root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
