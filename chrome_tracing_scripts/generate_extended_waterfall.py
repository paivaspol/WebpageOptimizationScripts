from argparse import ArgumentParser 
from collections import defaultdict

import constants
import simplejson as json
import os

NETWORK_RESOURCE_SEND_REQUEST = 'ResourceSendRequest'
NETWORK_RESOURCE_RECEIVE_RESPONSE = 'ResourceReceiveResponse'
NETWORK_RESOURCE_FINISH = 'ResourceFinish'

PARSING_PARSE_HTML = 'ParseHTML'
PARSING_PARSE_AUTHOR_STYLE_SHEET = 'ParseAuthorStyleSheet'

SCRIPT_EVALUATE_SCRIPT = 'EvaluateScript'
SCRIPT_FUNCTION_CALL = 'FunctionCall'
SCRIPT_TIMER_FIRE = 'TimerFire'

EVENT_INSTANT = 'I'
EVENT_COMPLETE = 'X'
EVENT_BEGIN = 'B'
EVENT_END = 'E'

PROCESSING_TIME = 'processing_time'

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = os.listdir(root_dir)
    for page in pages:
        print 'Processing: ' + page
        tracing_filename = os.path.join(root_dir, page, 'tracing_' + page)
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        if not (os.path.exists(tracing_filename) and os.path.exists(network_filename)):
            print 'here'
            continue
        url_timings, first_request_time, url_priorities = get_timings(tracing_filename, network_filename)
        output_to_file(url_timings, os.path.join(output_dir, page), first_request_time)
        output_priorities(url_priorities, os.path.join(output_dir, page))

def get_timings(tracing_filename, network_filename):
    url_to_resource_type = get_url_to_resource_type(network_filename)
    url_to_timings = defaultdict(lambda: defaultdict(list))
    url_to_request_priority = dict()
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
                    timing_name = val['name']
                    timestamp = int(val['ts'])
                    event_type = val['ph']  # The type of the event
                    if timing_name == NETWORK_RESOURCE_SEND_REQUEST or \
                        timing_name == PARSING_PARSE_AUTHOR_STYLE_SHEET or \
                        timing_name == SCRIPT_EVALUATE_SCRIPT:
                        try:
                            if first_request_time is None:
                                first_request_time = timestamp
                            else:
                                first_request_time = min(first_request_time, timestamp)
                            data = val['args']['data']
                            if timing_name == PARSING_PARSE_AUTHOR_STYLE_SHEET:
                                url = data['styleSheetUrl']
                            else:
                                url = data['url']

                            if timing_name == NETWORK_RESOURCE_SEND_REQUEST:
                                request_id = data['requestId']
                                priority = data['priority']
                                request_id_to_url[request_id] = url
                                url_to_request_priority[url] = priority
                            if event_type == EVENT_INSTANT:
                                url_to_timings[url][timing_name].append( timestamp )
                            elif event_type == EVENT_COMPLETE:
                                duration = int(val['dur'])
                                url_to_timings[url][timing_name].append( (timestamp,  timestamp + duration) )
                        except KeyError as e:
                            pass

                    elif timing_name == NETWORK_RESOURCE_RECEIVE_RESPONSE or \
                        timing_name == NETWORK_RESOURCE_FINISH:
                        data = val['args']['data']
                        request_id = data['requestId']
                        if request_id in request_id_to_url:
                            url = request_id_to_url[request_id]
                            url_to_timings[url][timing_name].append( timestamp )

                    elif timing_name == PARSING_PARSE_HTML:
                        if event_type == EVENT_BEGIN:
                            # Begin of ParseHTML event.
                            url = val['args']['beginData']['url']
                            parse_html_stack.append(url)
                            if parsed_html_timestamps[url][0] == -1 and \
                                parsed_html_timestamps[url][1] == -1:
                                parsed_html_timestamps[url][0] = timestamp
                        elif event_type == EVENT_END and len(parse_html_stack) > 0:
                            url = parse_html_stack.pop()
                            if url in parsed_html_timestamps:
                                parsed_html_timestamps[url][1] = max(parsed_html_timestamps[url][1], timestamp)

                    histogram[val['name']] += 1
                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()

        # Populate the ParseHTML times.
        for url, html_parse_time in parsed_html_timestamps.iteritems():
            url_to_timings[url][PARSING_PARSE_HTML].append((html_parse_time[0], html_parse_time[1]))
    return url_to_timings, first_request_time, url_to_request_priority

def output_priorities(url_priorities, output_dir):
    output_filename = os.path.join(output_dir, 'url_priorities.txt')
    with open(output_filename, 'wb') as output_file:
        for url, priority in url_priorities.iteritems():
            if url.startswith('data:') or len(url) == 0 or url == 'about:blank':
                continue
            output_file.write('{0} {1}\n'.format(url, priority))

def output_to_file(url_to_timings, output_dir, first_request_time):
    # The output contains 4 files:
    #   1) Resource send request
    #   2) Resource receive response
    #   3) Resource Finish
    #   4) Processing times
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    # Sort the urls by the request time.
    sorted_url_by_request_time = []
    for url, timings in url_to_timings.iteritems():
        sorted_url_by_request_time.append((url, timings[NETWORK_RESOURCE_SEND_REQUEST]))
    sorted_url_by_request_time.sort(key=lambda x: x[1])

    filenames = [ NETWORK_RESOURCE_SEND_REQUEST, \
                  NETWORK_RESOURCE_RECEIVE_RESPONSE, \
                  NETWORK_RESOURCE_FINISH, \
                  PROCESSING_TIME ]
    files = dict()
    for filename in filenames:
        files[filename] = open(os.path.join(output_dir, filename + '.txt'), 'wb')

    url_id = len(sorted_url_by_request_time)
    for url, _ in sorted_url_by_request_time:
        timings = url_to_timings[url]
        if url.startswith('data:') or len(url) == 0 or url == 'about:blank':
            continue
        # print timings
        for key, timing in timings.iteritems():
            # construct the line with this format: url url_id timings...
            for t in timing:
                output_line = '{0} {1} '.format(url, url_id)
                if type(t) is tuple:
                    output_line += str(t[0] - first_request_time) + ' ' + str(t[1] - first_request_time) + '\n'
                else:
                    output_line += str(t - first_request_time) + '\n'

                if key in files:
                    files[key].write(output_line)
                else:
                    files[PROCESSING_TIME].write(output_line)
        url_id -= 1

    # Close the files.
    for key, file_obj in files.iteritems():
        file_obj.close()

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
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
