r'''
Produces the expected number of requests based on the dummy HTML approach.
'''
from argparse import ArgumentParser
from collections import defaultdict
from urlmatcher import RoughUrlMatcher
from urllib.parse import urlparse

import common
import json
import os

def Main():
    for d in os.listdir(args.ha_crawled):
        requests_filename = os.path.join(args.ha_crawled, d, 'requests.json')
        response_bodies_filename = os.path.join(args.ha_crawled, d, 'response_bodies.json')
        referers_resources_mapping = GetRefererResourceMapping(requests_filename)
        crawled_urls = GetUrls(response_bodies_filename)

        network_filename = os.path.join(args.root_replay_dir, d, 'network_' + d)
        if not os.path.exists(network_filename):
            continue
        replay_referer_mapping = GetReplayRefererSubresourcesCount(network_filename)
        replay_referers = [ x for x in replay_referer_mapping if x is not None ]

        expected_resources = sum([ x[1] for x in replay_referer_mapping.items() ])
        matcher = RoughUrlMatcher()
        for r, r_subresources in referers_resources_mapping.items():
            if r in crawled_urls:
                continue

            match, _ = matcher.Match(r, replay_referers, matcher.SIFT4)

            # Don't create a dummy HTML for a URL that is never requested.
            # Need a rough matching.
            if r not in replay_referer_mapping:
                continue

            expected_resources -= replay_referer_mapping[r]
            expected_resources += len(referers_resources_mapping[r])

        print('{0} {1}'.format(d, expected_resources))


def GetReplayRefererSubresourcesCount(network_filename):
    '''Returns a dictionary mapping from referer --> subresource'''
    result = defaultdict(int)
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                referer = GetRefererFromNetworkEvent(e)
                result[referer] += 1
    return result


def GetRefererFromNetworkEvent(network_event):
    '''Returns the referer of the request.'''
    for header, value in network_event['params']['request']['headers'].items():
        if header == 'Referer':
            return value
    return None


def GetUrls(response_bodies):
    '''Returns a set of URLs.'''
    result = set()
    with open(response_bodies, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            result.add(entry['url'])
    return result


def GetRefererResourceMapping(requests_filename):
    '''Returns a dict mapping from the third-party referer to a list of URLs.'''
    result = defaultdict(list)
    css_referer_mapping = GetCssRefererMapping(requests_filename)
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            pageurl = entry['page']
            url = entry['url']
            payload = json.loads(entry['payload'])
            referer = ExtractRefererFromHAEntry(payload)

            # This is a CSS. Use the parent of the CSS instead.
            if referer in css_referer_mapping:
                referer = css_referer_mapping[referer]

            if not IsThirdPartyUrl(pageurl, referer):
                continue
            result[referer].append(url)
    return result


def GetCssRefererMapping(requests_filename):
    '''Returns a dictionary mapping from the CSS URL to its referer.'''
    mapping = {}
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            url = entry['url']
            payload = json.loads(entry['payload'])
            referer = ExtractRefererFromHAEntry(payload)
            if '.css' in url:
                mapping[url] = referer
    return mapping


def IsThirdPartyUrl(pageurl, url):
    '''Returns whether the passed URL is a third-party URL.'''
    escaped_page_url = common.escape_page(pageurl)
    parsed_url = urlparse(url)
    # print('escaped: {0} parsed.netloc: {1}'.format(escaped_page_url,
    #     parsed_url.netloc))
    return len(parsed_url.netloc) > 0 and escaped_page_url not in parsed_url.netloc


def ExtractRefererFromHAEntry(entry):
    '''Returns the request referer.'''
    headers = entry['request']['headers']
    for h in headers:
        if h['name'].lower() == 'referer':
            return h['value']
    return None


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_replay_dir')
    parser.add_argument('ha_crawled')
    args = parser.parse_args()
    Main()
