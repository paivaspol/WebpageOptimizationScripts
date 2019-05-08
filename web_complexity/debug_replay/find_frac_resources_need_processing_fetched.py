from argparse import ArgumentParser

import common
import json

def Main():
    crawled_urls = common.GetCrawledFiles(args.response_bodies_filename)
    url = next(iter(crawled_urls))
    crawled_urls = crawled_urls[url]
    requests_and_mime_type = GetRequestsAndContentTypes(args.requests_filename)
    for r, mime_type in requests_and_mime_type:
        if r in crawled_urls:
            continue
        print('{0} {1}'.format(r, mime_type))


def GetRequestsAndContentTypes(requests_filename):
    '''Returns a list of tuples: (url, mime_type).'''
    retval = []
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            payload = json.loads(entry['payload'])
            url = entry['url']
            mime_type = common.GetMimeTypeFromHAR(payload)
            retval.append((url, mime_type))
    return retval


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    parser.add_argument('response_bodies_filename')
    args = parser.parse_args()
    Main()
