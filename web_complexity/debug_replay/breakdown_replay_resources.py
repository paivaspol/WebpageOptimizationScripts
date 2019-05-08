r'''
Breaks down the resources that are seen in the replay run.

This is used to generate a stack bar chart where we breakdown the resources into
6 categories:
    1. Have response: 200
    2. Have response: 404
    3. Fetch Needed: 200
    4. Fetch Needed: 404
    5. Neither: 200
    6. Neither: 404

where neither represent resources that are not "Have response" nor "Fetch
Needed" (resources that are not in the HTTPArchive crawl).
'''
from argparse import ArgumentParser
from multiprocessing import Pool
from urllib.parse import urlparse
from urlmatcher import RoughUrlMatcher

import common
import json
import os
import urlmatcher

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
    '''Returns a length 7 tuple of the breakdown.

    Returns:
        [ len(urls_with_bodies_succeeded), len(urls_with_bodies_failed),
            len(fetched_urls_succeeded), len(fetched_urls_failed),
            len(neither_succeeded), len(neither_failed), total_urls ]
    '''
    urls_with_bodies, fetched_urls = common.GetUrlsFromHttpArchive(
            page_requests_filename, page_response_bodies_filename)
    status_code_mapping = common.StatusCodeMappingFromRun(page_experiment_network_filename)
    replay_urls = [ x for x in status_code_mapping.keys() ]
    if len(replay_urls) <= 2:
        return None

    matched_urls = set()

    urls_with_bodies_succeeded = []
    urls_with_bodies_failed = []
    urls_with_bodies_missing = []
    matcher = RoughUrlMatcher()
    for u in replay_urls:
        if u in matched_urls:
            continue

        matched_url = matcher.Match(u, urls_with_bodies, matcher.MAHIMAHI)
        if matched_url == urlmatcher.NO_MATCH:
            # Cannot find a match from the crawled URLs, so we skip this URL for
            # now.
            continue
        if status_code_mapping[u] == 200:
            urls_with_bodies_succeeded.append(u)
            matched_urls.add(u)
        else:
            urls_with_bodies_failed.append(u)
            matched_urls.add(u)

    fetched_urls_succeeded = []
    fetched_urls_failed = []
    fetched_urls_missing = []
    for u in replay_urls:
        if u in matched_urls:
            continue

        matched_url = matcher.Match(u, fetched_urls, matcher.MAHIMAHI)
        if matched_url is urlmatcher.NO_MATCH:
            # Cannot find a match from the crawled URLs, so we skip this URL for
            # now.
            continue
        elif status_code_mapping[u] == 200:
            fetched_urls_succeeded.append(u)
            matched_urls.add(u)
        else:
            fetched_urls_failed.append(u)
            matched_urls.add(u)

    neither_failed = 0
    neither_succeeded = 0
    for url in replay_urls:
        if url in matched_urls:
            continue
        status_code = status_code_mapping[url]
        if status_code == 200:
            neither_succeeded += 1
        else:
            neither_failed += 1
        matched_urls.add(url)
    # print('ReplayURLs: {0} matchedURLs: {1}'.format(len(replay_urls),
    #     len(matched_urls)))
    # print('Diff: {0}'.format(str(matched_urls - set(replay_urls))))

    total_urls = len(replay_urls)
    return [ len(urls_with_bodies_succeeded), len(urls_with_bodies_failed),
            len(fetched_urls_succeeded), len(fetched_urls_failed),
            neither_succeeded, neither_failed, total_urls ]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_response_dir')
    parser.add_argument('experiment_run')
    args = parser.parse_args()
    Main()
