from argparse import ArgumentParser
from urlparse import urlparse

import constants
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        # if 'fortune.com' not in page:
        #     continue
            
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        children_from_internal_resources, total_requests = find_children_from_internal_resources(network_filename, page)
        fraction = 1.0 * len(children_from_internal_resources) / total_requests
        print '{0} {1}'.format(page, fraction)

def find_children_from_internal_resources(network_filename, page):
    result = set()
    total_requests = 0
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event[constants.METHOD] == constants.NET_REQUEST_WILL_BE_SENT:
                total_requests += 1
                initiator = network_event[constants.PARAMS][constants.INITIATOR]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if url.startswith('data'):
                    continue

                if initiator[constants.TYPE] == 'script':
                    # Handle children of scripts
                    callframes = initiator[constants.STACK][constants.CALLFRAMES]
                    if len(callframes) > 0:
                        first_url = callframes[0][constants.URL]
                        hostname = urlparse(first_url).netloc
                        if hostname == page:
                            result.add(url)
                    else:
                        result.add(url)

                elif initiator[constants.TYPE] == 'parser':
                    # Need to figure out whether this request is from HTML parser or CSS parser.
                    # Use referer to do so.
                    initiator_url = initiator[constants.URL]
                    parsed_initiator_url = urlparse(initiator_url)
                    hostname = parsed_initiator_url.netloc

                    if hostname == page:
                        # Check the referer to make sure that this is either
                        # from the HTML or internal CSS.
                        if constants.REFERER in network_event[constants.PARAMS][constants.REQUEST][constants.HEADERS]:
                            referer = network_event[constants.PARAMS][constants.REQUEST][constants.HEADERS][constants.REFERER]
                            if urlparse(referer).netloc == page:
                                result.add(url)
    return result, total_requests

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
