from argparse import ArgumentParser

import common_module
import json

def main():
    with open(args.network_filename, 'rb') as input_file:
        completed_requests = []
        request_to_url = {}
        complete_count = 0
        requested_count = 0
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                req_id = e['params']['requestId']
                request_to_url[req_id] = url
                requested_count += 1
            elif e['method'] == 'Network.responseReceived':
                req_id = e['params']['requestId']
                url = e['params']['response']['url']
                if common_module.escape_url(url) == common_module.escape_url(args.main_page):
                    print 'Main HTML req ID: {0}'.format(req_id)
                    break
            elif e['method'] == 'Network.loadingFinished':
                req_id = e['params']['requestId']
                complete_count += 1
                completed_requests.append(req_id)
        print 'Requested: {0} Completed: {1}'.format(requested_count, complete_count)
        for req_id in completed_requests:
            print '\tCompleted: {0} {1}'.format(req_id, request_to_url[req_id])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    parser.add_argument('main_page')
    args = parser.parse_args()
    main()
