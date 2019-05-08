r'''
This script outputs tuples of URLs: <HTTP Archive URL, Matched URL>.
'''
from argparse import ArgumentParser
from multiprocessing import Pool
from urlmatcher import RoughUrlMatcher

import common
import os
import faulthandler

NOT_COMPUTED = '[NOT_COMPUTED]'

def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    pool = Pool()
    for d in os.listdir(args.requests_response_dir):
        page_requests_filename = os.path.join(args.requests_response_dir, d, 'requests.json')
        page_response_bodies_filename = os.path.join(args.requests_response_dir, d, 'response_bodies.json')
        page_experiment_network_filename = os.path.join(args.experiment_run, d, 'network_' + d)
        if not (os.path.exists(page_experiment_network_filename) and
            os.path.exists(page_requests_filename) and
            os.path.exists(page_response_bodies_filename)):
            continue
        page_output_filename = os.path.join(args.output_dir, d)
        # MatchUrlsForPage(d, page_requests_filename, page_response_bodies_filename,
        #                 page_experiment_network_filename, page_output_filename)
        pool.apply_async(MatchUrlsForPage, args=(
                d, page_requests_filename, page_response_bodies_filename,
                page_experiment_network_filename, page_output_filename),
                error_callback=common.HandleError)
    pool.close()
    pool.join()


def MatchUrlsForPage(pageurl, page_requests_filename,
        page_response_bodies_filename, page_experiment_network_filename,
        page_output_filename):
    '''Matches the urls for the page.'''
    print('Processing: ' + pageurl)
    urls_with_bodies, fetched_urls = common.GetUrlsFromHttpArchive(
            page_requests_filename, page_response_bodies_filename)
    all_httparchive_urls = [ x for x in urls_with_bodies | fetched_urls ]
    status_code_mapping = common.StatusCodeMappingFromRun(page_experiment_network_filename)
    replay_urls = status_code_mapping.keys()
    if len(replay_urls) <= 2:
        return

    matcher = RoughUrlMatcher()
    output = []
    for u in replay_urls:
        if not u.startswith('http'):
            continue

        # mahimahi_match = (NOT_COMPUTED, -1)
        mahimahi_match, mahimahi_match_score = matcher.Match(u, all_httparchive_urls,
                matcher.MAHIMAHI)
        levenshtein_match = (NOT_COMPUTED, -1)
        # levenshtein_match, levenshtein_match_score = matcher.Match(u, all_httparchive_urls,
        #         matcher.LEVENSHTEIN)
        # sift4_match = (NOT_COMPUTED, -1)
        sift4_match, sift4_match_score = matcher.Match(u, all_httparchive_urls,
                matcher.SIFT4)
        # last_path_token_match, last_path_token_score = (NOT_COMPUTED, -1)
        last_path_token_match, last_path_token_score = matcher.Match(
                u, all_httparchive_urls, matcher.MATCH_LAST_PATH_TOKEN)
        output.append((u, str(mahimahi_match), str(mahimahi_match_score),
            str(sift4_match), str(sift4_match_score),
            str(last_path_token_match), str(last_path_token_score),
            str(status_code_mapping[u])))
    with open(page_output_filename, 'w') as output_file:
        for o in output:
            output_file.write(' '.join(o) + '\n')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_response_dir')
    parser.add_argument('experiment_run')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
