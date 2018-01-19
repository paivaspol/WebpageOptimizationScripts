from argparse import ArgumentParser

import common_module
import json
import os

def main():
    for p in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue

        with open(network_filename, 'rb') as input_file:
            prefetch_urls = set()
            failed_urls = set()
            failed_urls_with_cache_hit = set()
            prefetch_urls_hit_cache = set()
            request_to_url = {}
            found_first_request = False
            completed_bytes_before_first_byte = 0
            prefetch_bytes_hit_cache = 0
            ttfb = -1
            for l in input_file:
                e = json.loads(l.strip())
                if e['method'] == 'Network.requestWillBeSent':
                    req_id = e['params']['requestId']
                    url = e['params']['request']['url']
                    request_to_url[req_id] = url
                    prefetched = 'Purpose' in e['params']['request']['headers'] and e['params']['request']['headers']['Purpose']
                    if prefetched:
                        prefetch_urls.add(url)
                    if common_module.escape_url(url) == p:
                        found_first_request = True

                elif e['method'] == 'Network.responseReceived':
                    req_id = e['params']['requestId']
                    url = e['params']['response']['url']
                    if url in prefetch_urls:
                        hit_cache = e['params']['response']['fromDiskCache']
                        if args.print_obj_details:
                            cache_status = 'CACHE_HIT' if hit_cache else 'CACHE_MISS'
                            print '\t{0}\t{1}\tURL: {2}'.format(req_id, cache_status, url)
                        if hit_cache:
                            prefetch_urls_hit_cache.add(url)
                            if url in failed_urls:
                                failed_urls_with_cache_hit.add(url)

                    if common_module.escape_url(url) == p:
                        found_first_request = True
                        ttfb = e['params']['response']['timing']['receiveHeadersEnd']

                elif e['method'] == 'Network.dataReceived':
                    req_id = e['params']['requestId']
                    if req_id not in request_to_url:
                        continue

                    url = request_to_url[req_id]
                    if url in prefetch_urls and url in prefetch_urls_hit_cache:
                        prefetch_bytes_hit_cache += data_size

                elif e['method'] == 'Network.loadingFinished':
                    req_id = e['params']['requestId']
                    if req_id not in request_to_url:
                        continue

                    url = request_to_url[req_id]
                    if url in prefetch_urls and not found_first_request:
                        data_size = e['params']['encodedDataLength']
                        completed_bytes_before_first_byte += data_size
                        if args.print_obj_details:
                            print '\t{0} {1} {2}'.format(req_id, url, data_size)

                elif e['method'] == 'Network.loadingFailed':
                    req_id = e['params']['requestId']
                    url = request_to_url[req_id]
                    if url in prefetch_urls:
                        failed_urls.add(url)
                    if args.print_obj_details:
                        print '\tFailed: {0}\t{1}'.format(req_id, url)
            if len(failed_urls) == 0:
                continue
            frac = 1.0 * len(failed_urls_with_cache_hit) / len(failed_urls)
            print '{0} {1} {2} {3} {4}'.format(p, len(failed_urls_with_cache_hit), len(failed_urls), frac, len(prefetch_urls))
            if args.print_details:
                print '''
                bytes_before_first_byte: {0}
                bytes_prefetch_hit_cache: {1}
                TTFB: {2}
                '''.format(completed_bytes_before_first_byte, prefetch_bytes_hit_cache, ttfb)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--print-obj-details', default=False, action='store_true')
    parser.add_argument('--print-details', default=False, action='store_true')
    args = parser.parse_args()
    main()
