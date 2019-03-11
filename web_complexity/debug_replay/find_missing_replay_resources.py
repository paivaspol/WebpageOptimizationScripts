from argparse import ArgumentParser
from collections import defaultdict
from urllib.parse import urlparse

import json
import os
import sys

def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    resp_sizes = None
    if args.output_resp_sizes is not None:
        resp_sizes = GetRespSizes(args.output_resp_sizes)

    all_replay_urls, all_replay_sizes, all_resource_types = \
        GetReplayURLs(args.root_dir)

    all_ha_urls, all_ha_resource_types = GetHAURLs(all_replay_urls.keys(), args.ha_all_urls)
    for pageurl, page_replay_urls in all_replay_urls.items():
        page_ha_urls = all_ha_urls[pageurl]
        page_ha_resource_types = all_ha_resource_types[pageurl]
        missing = GetDiff(page_ha_urls, page_replay_urls, compare_args=not args.ignore_args)
        extra = GetDiff(page_replay_urls, page_ha_urls, compare_args=not args.ignore_args)
        output_directory = os.path.join(args.output_dir, pageurl)
        if not os.path.exists(output_directory):
            os.mkdir(output_directory)

        page_resp_size = resp_sizes[pageurl] if resp_sizes is not None else None
        page_resource_types = all_resource_types[pageurl] if not None else None
        OutputToFile(missing, os.path.join(output_directory, 'missing'),
                page_resp_size, page_ha_resource_types)
        OutputToFile(extra, os.path.join(output_directory, 'extra'),
                page_resp_size, page_resource_types)
        OutputRespSizeCompare(page_replay_urls,
                os.path.join(output_directory, 'size_compare'),
                all_replay_sizes[pageurl], page_resp_size)


def OutputToFile(data, output_filename, resp_sizes, resource_types):
    '''
    Outputs the data to file.
    '''
    with open(output_filename, 'w') as output_file:
        running_size = 0
        missing_resp_size = 0
        for d in data:
            output_line = '{0}'.format(d)
            if resp_sizes is not None:
                if d in resp_sizes:
                    output_line += ' ' + str(resp_sizes[d])
                    running_size += resp_sizes[d]
                else:
                    output_line += ' [MISSING]'
                    missing_resp_size += 1

            if resource_types is not None:
                if d in resource_types:
                    output_line += ' ' + resource_types[d]
                else:
                    output_line += ' [RESOURCE_TYPE_MISSING]'

            output_file.write(output_line + '\n')

        if resp_sizes is not None:
            output_file.write('Total: ' + str(running_size) + '\n')
            output_file.write('Missing resp size: ' + str(missing_resp_size) + '\n')


def OutputRespSizeCompare(urls, output_filename, replay_resp_sizes,
        ha_resp_sizes):
    '''
    Outputs the comparison between replay size and HTTP Archive sizes.
    '''
    if replay_resp_sizes is None or ha_resp_sizes is None:
        return;

    with open(output_filename, 'w') as output_file:
        replay_running_size = 0
        ha_running_size = 0
        output_lines = ''
        for u in urls:
            if u not in replay_resp_sizes:
                continue

            replay_resp_size = replay_resp_sizes[u]
            replay_running_size += replay_resp_size
            output_line = '{0} {1}'.format(u, replay_resp_size)
            ha_resp_size = -1
            if u in ha_resp_sizes:
                ha_resp_size = ha_resp_sizes[u]
                output_line += ' ' + str(ha_resp_size)
                ha_running_size += ha_resp_size
            else:
                output_line += ' [MISSING]'
            if ha_resp_size == -1:
                continue

            diff = replay_resp_size - ha_resp_size
            output_lines += '{0} {1}\n'.format(output_line, diff)

        # output_file.write('Replay Total: ' + str(replay_running_size) +
        #         ' HA Total: ' + str(ha_running_size) + '\n')
        # output_file.write('Diff (replay - HA): ' +
        #         str() + '\n')
        output_file.write('{0} {1} {2}\n'.format(
            replay_running_size, ha_running_size, replay_running_size - ha_running_size))
        output_file.write(output_lines)


def GetRespSizes(resp_sizes_filename):
    '''
    Returns a dict from pageurl --> url --> respSize
    '''
    resp_sizes = defaultdict(dict)
    with open(resp_sizes_filename, 'r') as input_file:
        for i, l in enumerate(input_file):
            if i == 0:
                # Skip the header.
                continue
            # pageurl, url, resp_size, fetch_time
            splitted = l.strip().split()
            try:
                pageurl = splitted[0]
                url = splitted[1]
                resp_size = int(splitted[2])
                resp_sizes[EscapeURL(pageurl)][url] = resp_size
            except Exception as e:
                pass
    return resp_sizes


def GetDiff(first_urls, second_urls, compare_args=True):
    '''
    Returns difference between the first_urls and second_urls.
    '''
    if not compare_args:
        first_urls = RemoveArgsFromURLs(first_urls)
        second_url = RemoveArgsFromURLs(second_urls)
    return first_urls - second_urls


def RemoveArgsFromURLs(urls):
    '''
    Removes arguments from the given urls.
    '''
    retval = set()
    for url in urls:
        parsed_url = urlparse(url)
        final_url = parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
        retval.add(final_url)
    return retval


def GetHAURLs(replay_urls, ha_all_urls_file):
    all_urls = defaultdict(set)
    resource_types = defaultdict(dict)
    with open(ha_all_urls_file, 'r') as input_file:
        for i, l in enumerate(input_file):
            if i == 0:
                # Ignore first line.
                continue
            splitted = l.strip().split()
            pageurl = splitted[0]
            try:
                url = splitted[1]
                resource_type = splitted[4]
                pageurl = EscapeURL(pageurl)
                if pageurl not in replay_urls:
                    continue
                all_urls[pageurl].add(url)
                resource_types[pageurl][url] = resource_type
            except Exception as e:
                pass
    return all_urls, resource_types


def GetReplayURLs(root_dir):
    '''Returns a dict mapping from escaped page URL to a set of unique URLs.'''
    all_urls = {}
    all_sizes = {}
    all_types = {}
    for d in os.listdir(root_dir):
        network_filename = os.path.join(root_dir, d, 'network_' + d)
        page_urls, page_req_sizes, resource_types = GetURLs(network_filename)
        all_urls[d] = page_urls
        all_sizes[d] = page_req_sizes
        all_types[d] = resource_types
    return all_urls, all_sizes, all_types


def GetURLs(network_filename):
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


HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'
def EscapeURL(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('ha_all_urls')
    parser.add_argument('output_dir')
    parser.add_argument('--output-resp-sizes', default=None)
    parser.add_argument('--ignore-args', default=False, action='store_true')
    args = parser.parse_args()
    Main()
