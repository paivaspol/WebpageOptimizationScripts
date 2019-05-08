from argparse import ArgumentParser
from collections import defaultdict

import common
import json

def Main():
    with open(args.requests_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            pageurl = e['page']
            if args.page not in pageurl:
                continue

            entry = json.loads(e['payload'])
            referer = common.ExtractRefererFromHAEntry(entry)
            print('{0} {1}'.format(pageurl, referer))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    parser.add_argument('page')
    args = parser.parse_args()
    Main()
