'''
This script produces a list of random URLs from each of the
main HTML.
'''
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from urlparse import urldefrag

import os
import random

def Main():
    urls = [ x for x in GetURLs(args.onload_html) ]
    urls.sort()
    for u in urls:
        valid_url = GenerateValidURL(u, args.url_prefix)
        if valid_url == '':
            continue
        print valid_url


def GenerateValidURL(url, url_prefix):
    if url.startswith('http'):
        return url
    elif url.startswith('/'):
        return url_prefix + url
    else:
        return ''


def GetURLs(html_filename):
    '''
    Returns a list of num_urls URLs from the given HTML.
    '''
    with open(html_filename, 'r') as input_file:
        all_urls = set()
        html = input_file.read()
        soup = BeautifulSoup(html, 'html5lib')
        for l in soup.find_all('a'):
            link = l.get('href')
            if link is None or len(link) == 0:
                continue
            link = link.rstrip('/')
            all_urls.add(urldefrag(link)[0])
        return all_urls


def ReconstructURL(parsed_url):
    return parsed_url.scheme + parsed_url.netloc + parsed_url.path + parsed_url.params + parsed_url.fragment


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('onload_html')
    parser.add_argument('url_prefix')
    args = parser.parse_args()
    Main()
