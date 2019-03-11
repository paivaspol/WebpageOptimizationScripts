from argparse import ArgumentParser
from collections import defaultdict

import json

HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'
def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


def Main():
    all_reqs = []
    with open(args.json_file, 'r') as input_file:
        print('### Random first line')
        for l in input_file:
            req = json.loads(l)
            page = escape_page(req['page'])
            req_url = req['url']
            payload = json.loads(req['payload'])
            resp_size = payload['response']['content']['size']
            mime_type = payload['response']['content']['mimeType']
            print('{0} {1} {2} [TIME] {3}'.format(page, req_url, resp_size, mime_type))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('json_file')
    args = parser.parse_args()
    Main()
