from argparse import ArgumentParser
from collections import defaultdict

import common
import json

def Main():
    all_pages_crawled_files = common.GetCrawledFiles(args.response_bodies_filename)
    all_pages_referers = GetAllReferers(args.requests_filename)

    for pageurl, crawled in all_pages_crawled_files.items():
        if pageurl not in all_pages_referers:
            continue
        referers = all_pages_referers[pageurl]
        missing_from_crawl = referers - crawled
        print('{0} {1} {2} {3}'.format(pageurl,
            len(missing_from_crawl),
            len(referers),
            missing_from_crawl))


def GetAllReferers(requests_filename):
    '''Returns a dictionary mapping from page URL to a set of referers.'''
    result = defaultdict(set)
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            pageurl = entry['page']
            payload = json.loads(entry['payload'])
            referer = common.ExtractRefererFromHAEntry(payload)
            if referer is None or 'css' in referer:
                continue
            result[common.escape_page(pageurl)].add(referer)
    return result


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    parser.add_argument('response_bodies_filename')
    args = parser.parse_args()
    Main()
