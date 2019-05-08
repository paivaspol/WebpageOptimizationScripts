from argparse import ArgumentParser
from urlmatcher import RoughUrlMatcher

import json

def Main():
    replay_content_length = GetReplayContentLengths(args.network_filename)
    httparchive_content_length = GetHAContentLengths(args.requests_filename)
    httparchive_urls = [ u for u in httparchive_content_length.keys() ]
    urlmatcher = RoughUrlMatcher()
    for url in replay_content_length:
        matched = urlmatcher.NO_MATCH if url not in httparchive_content_length else url
        if matched == urlmatcher.NO_MATCH:
            matched, _ = urlmatcher.Match(url, httparchive_urls, urlmatcher.SIFT4)

        if matched not in httparchive_urls:
            continue
        # print('matched: ' + matched)
        print('{0} {1} {2}'.format(url, httparchive_content_length[matched], replay_content_length[url]))


def GetReplayContentLengths(network_filename):
    '''Returns a mapping from URL to content length.'''
    result = {}
    sum_content_length = 0
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.responseReceived':
                url = e['params']['response']['url']
                if not url.startswith('http'):
                    continue
                content_length = GetContentLengthFromReplay(e['params']['response']['headers'])
                result[url] = content_length
                sum_content_length += int(content_length)
    print('Sum Replay Content-Length: {0}'.format(sum_content_length))
    return result


def GetHAContentLengths(requests_filename):
    result = {}
    sum_content_length = 0
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            url = e['url']
            payload = json.loads(e['payload'])
            # content_length = # GetContentLengthFromHttpArchive(payload['response']['headers'])
            # content_length = payload['_object']
            content_length = payload['response']['content']['size']
            result[url] = content_length
            sum_content_length += int(content_length)
    print('Sum HA Content-Length: {0}'.format(sum_content_length))
    return result


def GetContentLengthFromHttpArchive(headers):
    for header in headers:
        if header['name'].lower() == 'content-length':
            return header['value']
    return -1


def GetContentLengthFromReplay(headers):
    for k, v in headers.items():
        if k.lower() == 'content-length':
            return v
    return -1


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    parser.add_argument('requests_filename')
    args = parser.parse_args()
    Main()
