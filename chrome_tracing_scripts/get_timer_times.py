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
SCRIPT_TIMER_INSTALL = 'TimerInstall'

EVENT_INSTANT = 'I'
EVENT_COMPLETE = 'X'
EVENT_BEGIN = 'B'
EVENT_END = 'E'

PROCESSING_TIME = 'processing_time'

def main(root_dir):

    pages = os.listdir(root_dir)
    for page in pages:
        tracing_filename = os.path.join(root_dir, page, 'tracing_' + page)
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(tracing_filename) and os.path.exists(network_filename)):
            print 'here'
            continue
        timer_install_time, timer_to_timestamp_dur = get_timings(tracing_filename, network_filename)
        timer_exec_time = sum([ x[1] for x in timer_to_timestamp_dur.values()])
        print '{0}\t{1}\t{2}\t{3}'.format(page, len(timer_install_time), len(timer_to_timestamp_dur), timer_exec_time)

def get_timings(tracing_filename, network_filename):
    timer_to_timestamp_dur = dict()
    timer_install_time = dict()
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
                    timing_name = val['name']
                    timestamp = int(val['ts'])
                    event_type = val['ph']  # The type of the event

                    if timing_name == SCRIPT_TIMER_FIRE:
                        if 'dur' in val:
                            timer_id = int(val['args']['data']['timerId'])
                            dur = int(val['dur'])
                            timer_to_timestamp_dur[timer_id] = (timestamp, dur)
                    elif timing_name == SCRIPT_TIMER_INSTALL:
                        timer_id = int(val['args']['data']['timerId'])
                        timer_install_time[timer_id] = timestamp

                    histogram[val['name']] += 1
                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()

    return timer_install_time, timer_to_timestamp_dur

def output_priorities(url_priorities, output_dir):
    output_filename = os.path.join(output_dir, 'url_priorities.txt')
    with open(output_filename, 'wb') as output_file:
        for url, priority in url_priorities.iteritems():
            if url.startswith('data:') or len(url) == 0 or url == 'about:blank':
                continue
            # output_file.write('{0} {1}\n'.format(urllib.quote(url), priority))
            output_file.write('{0} {1}\n'.format(url, priority))

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
