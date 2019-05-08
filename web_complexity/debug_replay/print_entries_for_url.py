from argparse import ArgumentParser

import json

def Main():
    with open(args.file, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            if args.url in entry['url']:
                print(l.strip())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('url')
    args = parser.parse_args()
    Main()
