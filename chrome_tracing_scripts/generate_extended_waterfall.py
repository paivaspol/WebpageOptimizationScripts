from argparse import ArgumentParser
from collections import defaultdict
from ResourceTiming import ResourceTiming

import constants
import json
import os
import sys

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = os.listdir(root_dir)
    for page in pages:
        print 'Processing: ' + page
        if 'huffingtonpost.com' in page:
            continue
        
        tracing_filename = os.path.join(root_dir, page, 'tracing_' + page)
        if not (os.path.exists(tracing_filename)):
            continue

        url_to_timings, first_request_time = parse_trace_file(tracing_filename)
        if not args.output_resources:
            output_to_file(url_to_timings, os.path.join(output_dir, page), first_request_time)
        else:
            for url, timing in url_to_timings.iteritems():
                print url
                print timing
                print timing.get_final_timings()

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
        sorted_url_by_request_time.append((url, timings.resource_send_request))
    sorted_url_by_request_time.sort(key=lambda x: x[1])

    filenames = [ constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST, \
                  constants.TRACING_NETWORK_RESOURCE_RECEIVE_RESPONSE, \
                  constants.TRACING_NETWORK_RESOURCE_FINISH, \
                  constants.TRACING_DISCOVERY_TIME, \
                  constants.TRACING_PRIORITIES, \
                  constants.TRACING_PROCESSING_TIME ]
    files = dict()
    for filename in filenames:
        files[filename] = open(os.path.join(output_dir, filename + '.txt'), 'wb')

    url_id = len(sorted_url_by_request_time)
    for url, _ in sorted_url_by_request_time:
        timings = url_to_timings[url].get_final_timings()
        if url.startswith('data:') or \
            len(url) == 0 or \
            url == 'about:blank' or \
            timings is None:
            continue
        # print timings
        for key, t in timings.iteritems():
            # construct the line with this format: url url_id timings...
            output_line = '{0} {1} '.format(url, url_id)
            if key != constants.TRACING_PRIORITIES:
                if type(t) is tuple:
                    output_line += str(t[0] - first_request_time) + ' ' + str(t[1] - first_request_time) + '\n'
                else:
                    output_line += str(t - first_request_time) + '\n'

                if key in files:
                    files[key].write(output_line)
                else:
                    files[PROCESSING_TIME].write(output_line)
            else:
                output_line = '{0} {1} '.format(url, url_id)
                files[key].write(output_line + t)

        url_id -= 1

    # Close the files.
    for key, file_obj in files.iteritems():
        file_obj.close()

def print_timing_sorted_by_time(timing):
    timing_dict = timing.__dict__
    result = []
    while len(timing_dict) > 4:
        min_time = sys.maxint
        min_key = ''
        for k, timings in timing_dict.iteritems():
            if type(timings) is list:
                if min_time > timings[0]:
                    min_time = timings[0]
                    min_key = k
        timing_dict[min_key].pop(0)
        if len(timing_dict[min_key]) == 0:
            del timing_dict[min_key]
        print '\t{0} {1}'.format(min_key, min_time)

def parse_trace_file(tracing_filename):
    first_request_time = None
    url_to_timings = dict()
    first_request_time = None
    with open(tracing_filename, 'rb') as input_file:
        event = ''
        cur_line = input_file.readline()
        histogram = defaultdict(lambda: 0)
        parse_html_stack = []
        blink_update_style_stack = []
        parsed_html_timestamps = defaultdict(lambda: [-1, -1])
        request_id_to_url = dict()
        script_eval_end = -1
        in_script_eval = False
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
                    category = val['cat']
                    timestamp = int(val['ts'])
                    event_type = val['ph']  # The type of the event
                    if timestamp > script_eval_end and in_script_eval:
                        in_script_eval = False

                    if timing_name == constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST or \
                        timing_name == constants.TRACING_PARSING_PARSE_AUTHOR_STYLE_SHEET or \
                        timing_name == constants.TRACING_SCRIPT_EVALUATE_SCRIPT or \
                        timing_name == constants.TRACING_NETWORK_RESOURCE_RECEIVE_RESPONSE or \
                        timing_name == constants.TRACING_NETWORK_RESOURCE_FINISH:
                        try:
                            first_request_time = timestamp if first_request_time is None else \
                                                 min(first_request_time, timestamp)
                            data = val['args']['data']
                            if timing_name == constants.TRACING_PARSING_PARSE_AUTHOR_STYLE_SHEET:
                                url = data['styleSheetUrl']
                            elif 'url' in data:
                                url = data['url']
                            else:
                                request_id = data['requestId']
                                url = request_id_to_url[request_id]

                            if event_type == constants.TRACING_EVENT_INSTANT:
                                getattr(url_to_timings[url], constants.to_underscore(timing_name)).append( timestamp )
                            elif event_type == constants.TRACING_EVENT_COMPLETE and \
                                timing_name == constants.TRACING_SCRIPT_EVALUATE_SCRIPT:
                                duration = int(val['dur'])
                                script_eval_end = timestamp + duration
                                in_script_eval = True
                                getattr(url_to_timings[url], constants.to_underscore('start_processing')).append( timestamp )
                                getattr(url_to_timings[url], constants.to_underscore('end_processing')).append( timestamp + duration )

                            if timing_name == constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST:
                                request_id = data['requestId']
                                request_id_to_url[request_id] = url
                                setattr(url_to_timings[url], 'request_id', data['requestId'])
                                setattr(url_to_timings[url], 'request_priority', data['priority'])
                        except KeyError as e:
                            pass

                    elif timing_name == constants.TRACING_PARSING_PARSE_HTML:
                        if event_type == constants.TRACING_EVENT_BEGIN:
                            # Begin of ParseHTML event.
                            url = val['args']['beginData']['url']
                            parse_html_stack.append(url)
                            if parsed_html_timestamps[url][0] == -1 and \
                                parsed_html_timestamps[url][1] == -1:
                                parsed_html_timestamps[url][0] = timestamp
                        elif event_type == constants.TRACING_EVENT_END and len(parse_html_stack) > 0:
                            url = parse_html_stack.pop()
                            if url in parsed_html_timestamps:
                                parsed_html_timestamps[url][1] = max(parsed_html_timestamps[url][1], timestamp)
                        # print 'len parse_html_stack: ' + str(len(parse_html_stack))

                    elif category == constants.TRACING_BLINK and \
                        timing_name == constants.TRACING_BLINK_REQUEST_RESOURCE:
                        url = val['args']['url']['url']
                        if url not in url_to_timings and \
                            not url.startswith('data:') and \
                            not url.startswith('about:blank'):
                            url_to_timings[url] = ResourceTiming(url)
                        # print timing_name + ' ' + str(timestamp) + ' ' + url + ' ' + str(in_script_eval)
                        if url in url_to_timings and \
                            (len(parse_html_stack) > 0 or \
                            len(url_to_timings[url].resource_discovered) == 0 or \
                            in_script_eval or \
                            len(blink_update_style_stack) > 0): # while we are parsing HTML or during script evaluation or during CSS update style
                            getattr(url_to_timings[url], 'resource_discovered').append( timestamp )

                    elif timing_name == constants.TRACING_BLINK_UPDATE_STYLE:
                        if event_type == constants.TRACING_EVENT_BEGIN:
                            blink_update_style_stack.append(0)
                        elif event_type == constants.TRACING_EVENT_END:
                            blink_update_style_stack.pop()

                    histogram[val['name']] += 1
                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()

        # Populate the ParseHTML times.
        for url, html_parse_time in parsed_html_timestamps.iteritems():
            if url in url_to_timings:
                url_to_timings[url].start_processing.append(html_parse_time[0])
                url_to_timings[url].end_processing.append(html_parse_time[1])
    return url_to_timings, first_request_time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--output-resources', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
