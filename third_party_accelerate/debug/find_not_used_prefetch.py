from argparse import ArgumentParser

import json
import os

def main():
    prefetch_urls = GetPrefetchUrls(args.prefetch_urls_dir)
    for p in os.listdir(args.root_dir):
        page_prefetch_urls = prefetch_urls[p]
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        request_counter, response_counter, request_hitting_cache = CheckPrefetchedUrls(network_filename, page_prefetch_urls)
        Output(p, request_counter, response_counter, request_hitting_cache)

def Output(p, request_counter, response_counter, request_hitting_cache):
    print 'page: ' + p
    urls_used = set()
    for url, count in request_counter.iteritems():
        print '\t{0}\t{1}\t{2}\t{3}'.format(url, count, response_counter[url], request_hitting_cache[url])
        if count >= 2:
            urls_used.add(url)
    print '\tused: {0}/{1} frac: {2}'.format(len(urls_used), len(request_counter), 1.0 * len(urls_used) / len(request_counter))


def CheckPrefetchedUrls(network_filename, page_prefetch_urls):
    request_counter = { url: 0 for url in page_prefetch_urls }
    response_counter = { url: 0 for url in page_prefetch_urls }
    request_hit_cache = { url: False for url in page_prefetch_urls }
    with open(network_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip()
            event = json.loads(l)
            if event['method'] == 'Network.requestWillBeSent':
                url = event['params']['request']['url'] 
                if url not in request_counter:
                    continue
                request_counter[url] += 1
            elif event['method'] == 'Network.responseReceived':
                url = event['params']['response']['url']
                if url not in response_counter:
                    continue
                response_counter[url] += 1

                if url not in request_counter:
                    continue
                request_hit_cache[url] = event['params']['response']['fromDiskCache']
    return request_counter, response_counter, request_hit_cache


def GetPrefetchUrls(prefetch_urls_dir):
    ''' Returns a dictionary of from the escaped page to list of urls being prefetched '''
    result = {}
    for p in os.listdir(prefetch_urls_dir):
        with open(os.path.join(prefetch_urls_dir, p), 'r') as input_file:
            prefetch_urls = set()
            for l in input_file:
                prefetch_urls.add(l.strip())
            result[p] = prefetch_urls
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('prefetch_urls_dir')
    args = parser.parse_args()
    main()
