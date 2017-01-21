from argparse import ArgumentParser

import constants
import os
import simplejson as json

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not os.path.exists(network_filename):
            continue
        timings = get_timings(network_filename)
        if check_overlap(timings):
            print 'PASS'
        else:
            print 'FAILED'
            for url, timing in timings:
                print '{0} {1} {2}'.format(url, timing[0], timing[1])

def check_overlap(timings):
    for i in range(0, len(timings)):
        for j in range(i + 1, len(timings)):
            if is_overlap(timings[i][1], timings[j][1]):
                return False
    return True


def is_overlap(first_int, second_int):
    return not (first_int[1] < second_int[0] or \
                second_int[1] < first_int[0])

def get_timings(network_filename):
    response_times = dict()
    request_id_to_url = dict()
    result = []
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            network_event = json.loads(line)
            if network_event[constants.METHOD] == constants.NET_RESPONSE_RECEIVED:
                if 's0.wp' in network_event[constants.PARAMS][constants.RESPONSE][constants.URL] or \
                    's1.wp' in network_event[constants.PARAMS][constants.RESPONSE][constants.URL] or \
                    's2.wp' in network_event[constants.PARAMS][constants.RESPONSE][constants.URL]:
                    url = network_event[constants.PARAMS][constants.RESPONSE][constants.URL]
                    if url not in response_times:
                        request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                        response_times[url] = float(network_event[constants.PARAMS][constants.TIMESTAMP])
                        request_id_to_url[request_id] = url
            elif network_event[constants.METHOD] == constants.NET_LOADING_FINISHED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                if request_id in request_id_to_url:
                    url = request_id_to_url[request_id]
                    ts = float(network_event[constants.PARAMS][constants.TIMESTAMP])
                    print '{0} {1} {2}'.format(url, response_times[url], ts)
                    result.append((url, (response_times[url], ts)))
    return sorted(result, key=lambda x: x[1][0])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
