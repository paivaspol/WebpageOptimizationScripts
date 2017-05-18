from argparse import ArgumentParser 
from collections import defaultdict

import constants
import simplejson as json
import os
import urllib

NETWORK_RESOURCE_SEND_REQUEST = 'ResourceSendRequest'
NETWORK_RESOURCE_RECEIVE_RESPONSE = 'ResourceReceiveResponse'
NETWORK_RESOURCE_FINISH = 'ResourceFinish'

PARSING_PARSE_HTML = 'ParseHTML'
PARSING_PARSE_AUTHOR_STYLE_SHEET = 'ParseAuthorStyleSheet'

SCRIPT_EVALUATE_SCRIPT = 'EvaluateScript'
SCRIPT_FUNCTION_CALL = 'FunctionCall'
SCRIPT_TIMER_FIRE = 'TimerFire'

EVENT_DISPATCH = 'EventDispatch'
DOM_CONTENT_LOADED = 'DOMContentLoaded'

EVENT_INSTANT = 'I'
EVENT_COMPLETE = 'X'
EVENT_BEGIN = 'B'
EVENT_END = 'E'

PROCESSING_TIME = 'processing_time'

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        print 'Processing: ' + page
        if 'huffingtonpost.com' in page:
            continue
        
        tracing_filename = os.path.join(root_dir, page, 'tracing_' + page)
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(tracing_filename) and os.path.exists(network_filename)):
            print 'here'
            continue
        dom_content_loaded = get_timings(tracing_filename, network_filename)
        print '{0} {1}'.format(page, dom_content_loaded)

def get_timings(tracing_filename, network_filename):
    first_request_time = None
    with open(tracing_filename, 'rb') as input_file:
        event = ''
        cur_line = input_file.readline()
        histogram = defaultdict(lambda: 0)
        parse_html_stack = []
        parsed_html_timestamps = defaultdict(lambda: [-1, -1])
        request_id_to_url = dict()
        while cur_line != '':
            if 'Tracing.dataCollected' in cur_line and \
                event != '':
                # process the current event.
                try:
                    parsed_event = json.loads(event)
                except Exception:
                    event = ''
                    continue
                params_values = parsed_event['params']['value']

                for val in params_values: # Iterate through each value.
                    name = val['name']
                    timestamp = int(val['ts'])
                    event_type = val['ph']  # The type of the event
                    if name == NETWORK_RESOURCE_SEND_REQUEST:
                        if first_request_time is None:
                            first_request_time = timestamp
                    elif name == EVENT_DISPATCH:
                        if 'args' in val and 'data' in val['args'] and \
                            'type' in val['args']['data'] and \
                            val['args']['data']['type'] == DOM_CONTENT_LOADED:
                           return timestamp - first_request_time
                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()
    return -1

def output_debugging(url_to_timings):
    for url, timings in url_to_timings.iteritems():
        print url
        for key, value in timings.iteritems():
            print '\t' + key + ': ' + str(value)

def get_url_to_resource_type(network_filename):
    result = dict()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == 'Network.responseReceived':
                url = network_event[constants.PARAMS][constants.RESPONSE][constants.URL]
                if url not in result:
                    result[url] = network_event[constants.PARAMS][constants.TYPE]
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
