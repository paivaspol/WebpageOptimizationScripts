from argparse import ArgumentParser

import constants
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        if page != 'fifa.com':
            continue
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        outstanding_events, request_id_to_url = count_events(network_filename)
        print page
        print str(len(outstanding_events)) + ' ' + str(outstanding_events)
        urls = [ request_id_to_url[x] for x in outstanding_events ]
        print urls

def count_events(network_filename):
    outstanding_requests = set()
    request_id_to_url = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            try:
                network_event = json.loads(json.loads(line))
            except:
                network_event = json.loads(line)
            if network_event[constants.METHOD] == constants.NET_REQUEST_WILL_BE_SENT:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                outstanding_requests.add(request_id)
                request_id_to_url[request_id] = url
            elif network_event[constants.METHOD] == constants.NET_LOADING_FINISHED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in outstanding_requests:
                    outstanding_requests.remove(request_id)
    return outstanding_requests, request_id_to_url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
