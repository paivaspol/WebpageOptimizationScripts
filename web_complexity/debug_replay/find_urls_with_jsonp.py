from argparse import ArgumentParser
from collections import defaultdict
from urllib.parse import urlparse, parse_qs

import json

def Main():
    total = 0
    with open(args.requests_filename, 'r') as input_file:
        jsonp_usage_count = defaultdict(int)
        for l in input_file:
            entry = json.loads(l.strip())
            pageurl = entry['page']
            url = entry['url']
            if UseJSONP(pageurl, url):
                jsonp_usage_count[pageurl] += 1
                total += 1

    for k, v in jsonp_usage_count.items():
        print('{0} {1}'.format(k, v))
    print('Total: {0}'.format(total))


def UseJSONP(page, url):
    '''This function analyzes the URL and returns whether it uses JSONP.

    Criterias:
        1. Check if the query parameters contain jquerycallback.
        TBD...
    '''
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    for query_key, query_vals_list in query_dict.items():
        if 'callback' in query_key:
            print('{0} {1}'.format(page, url))
            for v in query_vals_list:
                if 'jquery' in v.lower():
                    return True
    return False


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    args = parser.parse_args()
    Main()
