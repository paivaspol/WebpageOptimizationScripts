from argparse import ArgumentParser

import json
import os

def main():
    prefetch_urls = GetPrefetchUrls(args.prefetch_urls_dir)
    for p in os.listdir(args.root_dir):
        page_prefetch_urls = prefetch_urls[p]
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        request_counter = CheckPrefetchedUrls(network_filename, page_prefetch_urls)
        Output(p, request_counter)

def Output(p, request_counter):
    print 'page: ' + p
    urls_used = set()
    for url, count in request_counter.iteritems():
        print '\t{0}\t{1}'.format(url, count)
        if count >= 2:
            urls_used.add(url)
    print '\tused: {0}/{1} frac: {2}'.format(len(urls_used), len(request_counter), 1.0 * len(urls_used) / len(request_counter))


def CheckPrefetchedUrls(network_filename, page_prefetch_urls):
    request_counter = { url: 0 for url in page_prefetch_urls }
    with open(network_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip()
            event = json.loads(l)
            if event['method'] == 'Network.requestWillBeSent':
                url = event['params']['request']['url'] 
                if url not in request_counter:
                    continue
                request_counter[url] += 1
    return request_counter


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
