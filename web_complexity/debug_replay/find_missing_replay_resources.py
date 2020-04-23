from argparse import ArgumentParser
from collections import defaultdict
from urllib.parse import urlparse
from urlmatcher import RoughUrlMatcher
from multiprocessing import Pool

import common
import json
import os
import sys

WEBCOMPLEXITY = 'webcomplexity.com'
ARCHIVE_ORG = 'archive.org'

def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    pool = Pool()

    ha_onload_ts_ms = None
    if args.up_to_onload is not None:
        ha_onload_ts_ms = common.GetLoadTimesTsMs(args.up_to_onload)

    results = []
    for d in os.listdir(args.ha_splitted_url_root_dir):
        if args.debug is not None and args.debug not in d:
            continue
        requests_filename = os.path.join(args.ha_splitted_url_root_dir, d, 'requests.json')
        response_bodies_filename = os.path.join(args.ha_splitted_url_root_dir, d, 'response_bodies.json')
        page_replay_directory = os.path.join(args.replay_root_dir, d)
        output_directory = os.path.join(args.output_dir, d)
        if not (os.path.exists(requests_filename) and
                os.path.exists(page_replay_directory)):
            if args.debug is not None:
                print('Did not exec')
                print(page_replay_directory)
            continue
        result = pool.apply_async(GetPageUrlDiffs, args=(d,
            page_replay_directory, requests_filename, response_bodies_filename,
            output_directory, ha_onload_ts_ms))
        results.append(result)
    pool.close()
    pool.join()

    for r in results:
        r.get()


def GetPageUrlDiffs(pageurl, page_replay_directory, requests_filename,
        response_bodies_filename, output_directory, all_ha_onload_ts_ms):
    '''Returns a tuple containing missing resources and extra resources.

    Params:
      - network_filename: the network log
      - requests_filename: the JSON file exported from BigQuery
      - response_bodies_filename: the JSON file exported from BigQuery
    '''
    print('Processing: {0}'.format(pageurl))

    network_filename = os.path.join(page_replay_directory, 'network_' + pageurl)
    start_end_time_filename = os.path.join(page_replay_directory, 'start_end_time_' + pageurl)
    if not os.path.exists(network_filename):
        print('network_filename: ' + network_filename)
        return

    urlmatcher = RoughUrlMatcher()

    ha_onload_ts_ms = -1
    replay_onload_ms = -1
    if args.up_to_onload is not None:
        ha_onload_ts_ms = all_ha_onload_ts_ms[pageurl]
        replay_onload_ms = common.GetReplayPltMs(start_end_time_filename)

    ha_urls, ha_resource_sizes, ha_resource_types = GetHAUrls(requests_filename,
            onload_ts_ms=ha_onload_ts_ms)
    replay_urls, replay_resource_sizes, replay_resource_types = \
        GetReplayUrls(network_filename, onload_time_ms=replay_onload_ms)
    urls_with_bodies = common.GetResponseBodiesUrls(response_bodies_filename)

    # Missing resources: resources that were requested in HTTPArchive crawl,
    # but not in replay.
    #
    # Find whether replay URL match a HA resource, if it matched then it is not
    # a missing resource.
    ha_left_for_matching = set(ha_urls)
    if args.debug:
        print(len(ha_left_for_matching))
    ha_matched = set()
    for replay_url in replay_urls:
        matched, _ = urlmatcher.Match(replay_url, ha_left_for_matching, urlmatcher.SIFT4)
        if matched == urlmatcher.NO_MATCH:
            continue
        ha_matched.add(matched)
        ha_left_for_matching.remove(matched)
    missing = [ url for url in ha_urls - ha_matched ]
    missing.sort()

    # Extra resources: resources that were not requested in HTTPArchive crawl,
    # but was requested in replay.
    #
    # Find whether HA URL match a replay resource, if it matched then it is not
    # an extra resource.
    replay_left_for_matching = set(replay_urls)
    replay_matched = set()
    for ha_url in ha_urls:
        matched, _ = urlmatcher.Match(ha_url, replay_left_for_matching, urlmatcher.SIFT4)
        if matched == urlmatcher.NO_MATCH:
            continue
        replay_matched.add(matched)
        replay_left_for_matching.remove(matched)
    extra = [ url for url in replay_urls - replay_matched ]
    extra.sort()

    if not os.path.exists(output_directory):
        os.mkdir(output_directory)

    OutputToFile(missing, os.path.join(output_directory, 'missing'),
            ha_resource_sizes, ha_resource_types,
            urls_with_response=urls_with_bodies)
    OutputToFile(extra, os.path.join(output_directory, 'extra'),
            replay_resource_sizes, replay_resource_types)


def OutputToFile(data, output_filename, resp_sizes={}, resource_types={},
        urls_with_response=None):
    '''
    Outputs the data to file.
    '''
    with open(output_filename, 'w') as output_file:
        running_size = 0
        missing_resp_size = 0
        for d in data:
            output_line = '{0}'.format(d)
            if d in resource_types:
                res_type = resource_types[d]
                if len(res_type) == 0:
                    res_type = '[RESOURCE_TYPE_MISSING]'
                output_line += ' ' + res_type
            else:
                output_line += ' [RESOURCE_TYPE_MISSING]'

            if d in resp_sizes:
                output_line += ' ' + str(resp_sizes[d])
                running_size += resp_sizes[d]
            else:
                output_line += ' [MISSING_RESP_SIZE]'
                missing_resp_size += 1

            if urls_with_response is not None and d in urls_with_response:
                output_line += ' HAS_RESPONSE'
            elif urls_with_response is not None and d not in urls_with_response:
                output_line += ' FETCHED'

            output_file.write(output_line + '\n')

        if resp_sizes is not None and args.print_summary:
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


def GetHAUrls(ha_all_urls_file, onload_ts_ms=-1):
    '''Returns a tuple of (a set of HTTP Archive URLs, dictionary of resource
    types.'''
    if args.debug:
        print('Onload: ' + str(onload_ts_ms))
    all_urls = set()
    resource_sizes = {}
    resource_types = {}
    with open(ha_all_urls_file, 'r') as input_file:
        for i, l in enumerate(input_file):
            entry = json.loads(l)
            pageurl = common.escape_page(entry['page'])
            url = entry['url']
            payload = json.loads(entry['payload'])
            resource_type = payload['response']['content']['mimeType']
            resource_size = payload['response']['content']['size']
            resource_sizes[url] = resource_size
            start_ts_epoch_ms = common.GetTimestampSinceEpochMs(payload['startedDateTime'])
            load_time_ms = payload['time'] if 'time' in payload else -1
            # Only get up to onload. onload_ts_ms == -1 means get all requests.
            if onload_ts_ms != -1 and (load_time_ms == -1 or start_ts_epoch_ms +
                    load_time_ms > onload_ts_ms):
                continue

            if payload['response']['status'] == 206:
                continue

            all_urls.add(url)
            resource_types[url] = resource_type
    return all_urls, resource_sizes, resource_types


def GetReplayUrls(network_filename, onload_time_ms=-1):
    '''Returns a set of unique URLs seen in the network file.'''
    with open(network_filename, 'r') as input_file:
        req_ids = set()
        resource_types = {}
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
                req_id = e['params']['requestId']
                url = e['params']['request']['url']
                timestamp_ms = e['params']['timestamp'] * 1000 # Convert to ms
                if first_ts_ms == -1:
                    first_ts_ms = timestamp_ms
                if WEBCOMPLEXITY in url or ARCHIVE_ORG in url or not url.startswith('http'):
                    continue

                # Cut at load time.
                if onload_time_ms != -1 and timestamp_ms - first_ts_ms > onload_time_ms:
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
                resource_types[url] = e['params']['type']
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
                if onload_time_ms != -1 and timestamp_ms - first_ts_ms > onload_time_ms:
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

    # with open(network_filename, 'r') as input_file:
    #     urls = set()
    #     size_map = {}
    #     req_id_to_url = {}
    #     first_ts_ms = -1
    #     for l in input_file:
    #         e = json.loads(l.strip())
    #         if e['method'] == 'Network.requestWillBeSent':
    #             ts_ms = e['params']['timestamp'] * 1000.0
    #             if first_ts_ms == -1:
    #                 first_ts_ms = ts_ms

    #             # This happens after onload. Ignore.
    #             if onload_time_ms != -1 and ts_ms > first_ts_ms + onload_time_ms:
    #                 continue

    #             req_id = e['params']['requestId']
    #             url = e['params']['request']['url']
    #             if not url.startswith('http') or \
    #                     WEBCOMPLEXITY in url or \
    #                     ARCHIVE_ORG in url:
    #                 continue

    #             req_id_to_url[req_id] = url
    #             # resource_types[url] = e['params']['type']
    #             # urls.add(url)
    #         elif e['method'] == 'Network.responseReceived':
    #             url = e['params']['response']['url']
    #             if e['params']['response']['status'] == 200 and url in requested:
    #                 # print(e)
    #                 urls.add(url)
    #         elif e['method'] == 'Network.loadingFinished':
    #             req_id = e['params']['requestId']
    #             if req_id not in req_id_to_url:
    #                 continue
    #             url = req_id_to_url[req_id]
    #             size = e['params']['encodedDataLength']
    #             size_map[url] = int(size)
    print(urls)
    return urls, url_to_size, resource_types


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('ha_splitted_url_root_dir')
    parser.add_argument('replay_root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-args', default=False, action='store_true')
    parser.add_argument('--up-to-onload', default=None)
    parser.add_argument('--print-summary', default=False, action='store_true')
    parser.add_argument('--debug', default=None)
    args = parser.parse_args()
    Main()
