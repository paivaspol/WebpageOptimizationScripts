from argparse import ArgumentParser

import constants
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            print 'here'
            continue
        resources, all_requested = get_resources(network_filename)
        for r in resources:
            print r
        for r in all_requested:
            print r

def get_resources(network_filename):
    requested_resources = dict()
    all_requested = []
    num_resources = 0
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == constants.NET_REQUEST_WILL_BE_SENT:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                requested_resources[request_id] = url
                all_requested.append(url)
            elif network_event[constants.METHOD] == constants.NET_LOADING_FINISHED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in requested_resources:
                    del requested_resources[request_id]
                    num_resources += 1
    print '# Resources: ' + str(num_resources)
    return [ val for _, val in requested_resources.iteritems() ], all_requested

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
