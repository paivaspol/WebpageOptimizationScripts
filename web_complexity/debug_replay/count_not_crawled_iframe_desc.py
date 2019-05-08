from argparse import ArgumentParser
from collections import defaultdict
from urlmatcher import RoughUrlMatcher

import common
import json
import os

DEBUG_PAGE = 'workle.ru'

def Main():
    # 1. Generate page --> referers --> URL count from HA crawl.
    all_pages_ha_desc_count = GetHAPagesReferersCount(args.requests_filename)
    all_pages_crawled_desc_count, all_pages_not_crawled_desc_count = \
        SplitCrawledAndNotCrawledIframes(all_pages_ha_desc_count,
                args.response_bodies_filename)

    # 2. Generate page --> referers --> URL count from replay.
    all_pages_replay_desc_count = GetReplayPagesReferersCount(args.replay_dir)

    # 3. Get the diffs.
    crawled_iframes_desc_count = \
        GetDescendantsComparison(all_pages_crawled_desc_count,
                all_pages_replay_desc_count, '[CRAWLED]')
    not_crawled_iframes_desc_count = \
        GetDescendantsComparison(all_pages_not_crawled_desc_count,
                all_pages_replay_desc_count, '[NOT_CRAWLED]')

    OutputToFiles(args.output_dir, crawled_iframes_desc_count,
            not_crawled_iframes_desc_count)


def OutputToFiles(output_dir, crawled_iframes_desc_count,
        not_crawled_iframes_desc_count):
    '''Outputs to the files.'''
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with open(os.path.join(output_dir, 'crawled'), 'w') as output_file:
        for pageurl, desc_count in crawled_iframes_desc_count.items():
            output_file.write('{0} {1} {2}\n'.format(pageurl, desc_count[0],
                desc_count[1]))

    with open(os.path.join(output_dir, 'not_crawled'), 'w') as output_file:
        for pageurl, desc_count in not_crawled_iframes_desc_count.items():
            output_file.write('{0} {1} {2}\n'.format(pageurl, desc_count[0],
                desc_count[1]))


def GetDescendantsComparison(all_pages_ha_desc_count,
        all_pages_replay_desc_count, debug_string):
    '''Returns a dict mapping from pageurl --> ( desc count of HA iframes, desc
    count of replay ).'''
    urlmatcher = RoughUrlMatcher()
    result = {}
    for pageurl, referer_to_replay_desc_count in all_pages_replay_desc_count.items():
        if args.debug and DEBUG_PAGE in pageurl:
            continue

        if pageurl not in all_pages_ha_desc_count:
            continue
        page_ha_desc_count = all_pages_ha_desc_count[pageurl]
        page_ha_referers = [ r for r in page_ha_desc_count.keys() ]
        for referer, replay_desc_count in referer_to_replay_desc_count.items():
            print('{0} Matching: {1} with {2}'.format(debug_string, referer, page_ha_referers))
            matched_ha_referer, match_score = urlmatcher.Match(referer, page_ha_referers,
                    urlmatcher.SIFT4)
            if matched_ha_referer not in page_ha_desc_count:
                print('[WARN] matched_ha_referer ({0}) not found...'.format(matched_ha_referer))
                continue
            ha_desc_count = page_ha_desc_count[matched_ha_referer]
            result[pageurl] = ( ha_desc_count, replay_desc_count )
    return result


def GetHAPagesReferersCount(requests_filename):
    '''Returns a double map from the page to the iframe descendant count.'''
    result = defaultdict(lambda: defaultdict(int))
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            pageurl = common.escape_page(e['page'])
            entry = json.loads(e['payload'])
            referer = common.ExtractRefererFromHAEntry(entry)
            if referer is None or referer == pageurl or 'css' in referer:
                # Ignore anything that is not the main HTML.
                continue
            result[pageurl][referer] += 1
    return result


def SplitCrawledAndNotCrawledIframes(page_referers_mapping,
        response_bodies_filename):
    '''Returns a tuple of double dictionary mapping from page --> iframe -->
    desc count.

    First tuple is the crawled iframes, and the second tuple is the not crawled
    ones.'''
    all_pages_crawled_files = common.GetCrawledFiles(response_bodies_filename)
    crawled = {}
    not_crawled = {}
    for page, referers_count_mapping in page_referers_mapping.items():
        if args.debug and DEBUG_PAGE in page:
            continue

        if page not in all_pages_crawled_files:
            continue
        page_crawled_files = all_pages_crawled_files[page]
        crawled[page] = {}
        not_crawled[page] = {}
        for referer, count in referers_count_mapping.items():
            if referer in page_crawled_files:
                crawled[page][referer] = count
            else:
                not_crawled[page][referer] = count
    return (crawled, not_crawled)


def GetReplayPagesReferersCount(replay_dir):
    '''Returns a double map from the page to the iframe descendant count.'''
    result = {}
    for d in os.listdir(replay_dir):
        if args.debug and DEBUG_PAGE in d:
            continue

        network_filename = os.path.join(replay_dir, d, 'network_' + d)
        result[d] = GetThirdPartyDescendantsMapping(d, network_filename)
    return result


def GetThirdPartyDescendantsMapping(page, network_filename):
    '''Returns a map from an iframe to the descendant count.'''
    result = defaultdict(int)
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                if 'Referer' not in e['params']['request']['headers']:
                    continue

                referer = e['params']['request']['headers']['Referer']
                if common.escape_page(referer) == page or 'css' in referer:
                    continue
                result[referer] += 1
    return result


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    parser.add_argument('response_bodies_filename')
    parser.add_argument('replay_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()
    Main()
