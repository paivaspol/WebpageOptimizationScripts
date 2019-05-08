import json

from argparse import ArgumentParser

def Main():
    with open(args.requests_json, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            if args.page_url in entry['page']:
                print(entry)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_json')
    parser.add_argument('page_url')
    args = parser.parse_args()
    Main()

