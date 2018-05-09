from argparse import ArgumentParser

import json
import os
import shutil

def Main():
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    pages_description = GetPageDescription(args.page_description)
    for c in pages_description:
        pages_type = c['type']
        os.mkdir(os.path.join(args.output_dir, c['type']))
        urls = c['urls']
        for u in urls:
            escaped_url = EscapeURL(u)
            network_filename = os.path.join(args.root_dir, escaped_url, 'network_' + escaped_url)
            try:
                page_requests = GetRequests(network_filename)
                with open(os.path.join(args.output_dir, c['type'], escaped_url), 'w') as output_file:
                    for r in page_requests:
                        output_file.write(r + '\n')
            except Exception as e:
                print e
                continue


def EscapeURL(url):
    HTTP_PREFIX = 'http://'
    HTTPS_PREFIX = 'https://'
    WWW_PREFIX = 'www.'

    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


def GetRequests(network_filename):
    with open(network_filename, 'r') as input_file:
        seen_urls = set()
        urls = []
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                if url in seen_urls or not url.startswith('http'):
                    continue
                urls.append(url)
                seen_urls.add(url)
        return urls


def GetPageDescription(page_desc_filename):
    with open(page_desc_filename, 'r') as input_file:
        return json.loads(input_file.read())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_description')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
