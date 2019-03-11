from argparse import ArgumentParser

import common
import json

def Main():
    with open(args.request_info, 'r') as input_file:
        ips = set()
        for l in input_file:
            r = json.loads(l.strip())
            pageurl = common.escape_page(r['pageurl'])
            if args.page not in pageurl:
                continue

            resource_url = r['url']
            payload = json.loads(r['payload'])
            if '_ip_addr' not in payload:
                continue

            ips.add(payload['_ip_addr'])
    for ip in ips:
        print(ip)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('request_info')
    parser.add_argument('page')
    args = parser.parse_args()
    Main()
