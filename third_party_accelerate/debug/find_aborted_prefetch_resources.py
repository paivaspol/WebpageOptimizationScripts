from argparse import ArgumentParser

import json
import os

def main():
    prefetch_urls = GetPrefetchUrls(args.prefetch_urls_dir)
    for p in os.listdir(args.root_dir):
        page_prefetch_urls = prefetch_urls[p]
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        cancelled_requests, cancelled_urls, urls_hit_cache = CheckPrefetchedUrls(network_filename, page_prefetch_urls)
        Output(p, cancelled_requests, cancelled_urls, urls_hit_cache, page_prefetch_urls)

def Output(p, failed_prefetches, failed_prefetches_urls, urls_hit_cache, prefetch_urls):
    if len(prefetch_urls) == 0:
        return
    frac = 1.0 * len(failed_prefetches) / len(prefetch_urls)
    failed_prefetch_cache_hit = 0
    resource_details = ''
    for url in failed_prefetches_urls:
        if url in urls_hit_cache:
            failed_prefetch_cache_hit += 1
        prefix = 'CACHE_HIT' if url in urls_hit_cache else 'CACHE_MISS'
        resource_details += '\t' + prefix + '\t' + url + '\n'
    prefetch_cache_miss = len(prefetch_urls - urls_hit_cache)
    summary = '''Page: {0}\tprefetch_urls: {1}
    Failed Prefetch: {2}\tfrac:{3}
    prefetch_hit_cache: {4}\tprefetch_cache_miss: {5}\tfailed_prefetch_cache_hit: {6}
    '''.format(p, len(prefetch_urls), len(failed_prefetches_urls), frac, len(urls_hit_cache), prefetch_cache_miss, failed_prefetch_cache_hit)
    print summary
    print resource_details


def CheckPrefetchedUrls(network_filename, page_prefetch_urls):
    cancelled_requests = set()
    cancelled_urls = []
    prefetch_request_ids = set()
    urls_hit_cache = set()
    req_id_to_url = {}
    with open(network_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip()
            event = json.loads(l)
            if event['method'] == 'Network.requestWillBeSent':
                req_id = event['params']['requestId']
                url = event['params']['request']['url'] 
                if url not in page_prefetch_urls:
                    continue
                if 'Purpose' not in event['params']['request']['headers']:
                    continue
                prefetch_request_ids.add(req_id)
                req_id_to_url[req_id] = url
            elif event['method'] == 'Network.responseReceived':
                url = event['params']['response']['url']
                if url not in page_prefetch_urls:
                    continue
                if event['params']['response']['fromDiskCache']:
                    urls_hit_cache.add(url)

            elif event['method'] == 'Network.loadingFailed':
                req_id = event['params']['requestId']
                if req_id in prefetch_request_ids:
                    cancelled_requests.add(req_id)
                    cancelled_urls.append(req_id_to_url[req_id])

    return cancelled_requests, cancelled_urls, urls_hit_cache


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
