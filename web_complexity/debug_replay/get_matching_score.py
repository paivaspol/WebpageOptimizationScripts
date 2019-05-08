from argparse import ArgumentParser
from multiprocessing import Pool
from urlmatcher import RoughUrlMatcher

import common
import os
import urlmatcher

TOP_N = 5

def Main():
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    pool = Pool()
    for i, d in enumerate(os.listdir(args.requests_response_dir)):
        page_requests_filename = os.path.join(args.requests_response_dir, d, 'requests.json')
        page_response_bodies_filename = os.path.join(args.requests_response_dir, d, 'response_bodies.json')
        page_experiment_network_filename = os.path.join(args.experiment_run, d, 'network_' + d)
        if not (os.path.exists(page_experiment_network_filename) and
            os.path.exists(page_requests_filename) and
            os.path.exists(page_response_bodies_filename)):
            continue
        page_output_filename = os.path.join(args.output_dir, d)
        # GetTop5Match(d, page_requests_filename, page_response_bodies_filename,
        #                 page_experiment_network_filename, page_output_filename)
        # if i == 5:
        #     break
        pool.apply_async(GetTop5Match, args=(
                d, page_requests_filename, page_response_bodies_filename,
                page_experiment_network_filename, page_output_filename),
                error_callback=common.HandleError)
    pool.close()
    pool.join()


def GetTop5Match(pageurl, page_requests_filename,
        page_response_bodies_filename, page_experiment_network_filename,
        page_output_filename):
    '''Finds the top 5 match for each of the URL and outputs the score.'''
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
        sift4_matches = matcher.GetMatchingScores(u, all_httparchive_urls,
                matcher.SIFT4)
        sorted_matches = sorted(sift4_matches.items(), key=lambda x: x[1])
        top_matches = sorted_matches[:TOP_N]
        if top_matches[0][1] != 0 and \
            top_matches[0][1] != urlmatcher.DEFAULT_EDIT_DISTANCE:
            output.append(FormatOutput(u, top_matches))

    with open(page_output_filename, 'w') as output_file:
        for o in output:
            output_file.write(o + '\n')


def FormatOutput(url, top_matches):
    '''Returns a string that represents the output of the URL.

    The output is in the following format:
        Replay URL: [URL]\n
        \t[matching_url] [matching_score]
        ...
        \t[matching_url] [matching_score]
    '''
    top_matches_string = ''
    for top_match in top_matches:
        top_matches_string += '\t{0} {1}\n'.format(top_match[0], top_match[1])
    return 'Replay URL: {0}\n{1}'.format(url, top_matches_string)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_response_dir')
    parser.add_argument('experiment_run')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
