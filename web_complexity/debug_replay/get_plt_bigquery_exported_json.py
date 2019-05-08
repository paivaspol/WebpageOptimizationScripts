from argparse import ArgumentParser

import common
import json

def Main():
    with open(args.pages_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            payload = json.loads(entry['payload'])
            load_time = payload['_loadTime']
            escaped_url = common.escape_page(entry['url'])
            print('{0} {1}'.format(escaped_url, load_time))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_filename')
    args = parser.parse_args()
    Main()
