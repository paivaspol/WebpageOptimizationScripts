from argparse import ArgumentParser

import json

def main():
    with open(args.network_filename, 'rb') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                print '{0}\t{1}'.format(e['params']['requestId'], e['params']['request']['url'])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    main()
