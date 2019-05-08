r'''
Breaks down the resources that are seen in the HTTPArchive crawl.

This is used to generate a stack bar chart where we breakdown the resources into
6 categories:
    1. Have response: 200
    2. Have response: 404
    3. Fetch Needed: 200
    4. Fetch Needed: 404
    5. Not requested: 200
    6. Not requested: 404
'''
from argparse import ArgumentParser
from multiprocessing import Pool
from urllib.parse import urlparse
from urlmatcher import RoughUrlMatcher

import common
import json
import os

def Main():
    results = []
    pool = Pool()
    for d in os.listdir(args.requests_response_dir):
        page_requests_filename = os.path.join(args.requests_response_dir, d, 'requests.json')
        page_response_bodies_filename = os.path.join(args.requests_response_dir, d, 'response_bodies.json')
        page_experiment_network_filename = os.path.join(args.experiment_run, d, 'network_' + d)
        if not (os.path.exists(page_experiment_network_filename) and
            os.path.exists(page_requests_filename) and
            os.path.exists(page_response_bodies_filename)):
            continue
        # breakdown = GetBreakdownForPage(
        #         d, page_requests_filename, page_response_bodies_filename, page_experiment_network_filename)
        result = pool.apply_async(GetBreakdownForPage, args=(
                d, page_requests_filename, page_response_bodies_filename,
                page_experiment_network_filename))
        results.append((d, result))
    pool.close()
    pool.join()

    for pageurl, r in results:
        breakdown = r.get()
        if breakdown is None:
            continue
        breakdown = [ str(b) for b in breakdown ]
        breakdown_str = ' '.join(breakdown)
        print('{0} {1}'.format(pageurl, breakdown_str))


def GetBreakdownForPage(pageurl, page_requests_filename,
        page_response_bodies_filename, page_experiment_network_filename):
    '''Returns a length 7 tuple of the breakdown.'''
    urls_with_bodies, fetched_urls = common.GetUrlsFromHttpArchive(
            page_requests_filename, page_response_bodies_filename)
    status_code_mapping = common.StatusCodeMappingFromRun(page_experiment_network_filename)
    replay_urls = [ x for x in status_code_mapping.keys() ]
    if len(replay_urls) <= 2:
        return None

    urls_with_bodies_succeeded = []
    urls_with_bodies_failed = []
    urls_with_bodies_missing = []
    matcher = RoughUrlMatcher()
    for u in urls_with_bodies:
        matched_url = matcher.Match(u, replay_urls, matcher.MAHIMAHI)
        if matched_url is None:
            urls_with_bodies_missing.append(u)
        elif status_code_mapping[matched_url] == 200:
            urls_with_bodies_succeeded.append(matched_url)
        else:
            urls_with_bodies_failed.append(matched_url)

    fetched_urls_succeeded = []
    fetched_urls_failed = []
    fetched_urls_missing = []
    for u in fetched_urls:
        matched_url = matcher.Match(u, replay_urls, matcher.MAHIMAHI)
        if matched_url is None:
            fetched_urls_missing.append(matched_url)
        elif status_code_mapping[matched_url] == 200:
            fetched_urls_succeeded.append(matched_url)
        else:
            fetched_urls_failed.append(matched_url)

    total_urls = len(urls_with_bodies) + len(fetched_urls)
    return [ len(urls_with_bodies_succeeded), len(urls_with_bodies_failed),
            len(urls_with_bodies_missing), len(fetched_urls_succeeded),
            len(fetched_urls_failed), len(fetched_urls_missing), total_urls ]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_response_dir')
    parser.add_argument('experiment_run')
    args = parser.parse_args()
    Main()
