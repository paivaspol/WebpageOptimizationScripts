from argparse import ArgumentParser
from collections import defaultdict

import constants
import json
import os

def parse_trace_file(tracing_filename):
    with open(tracing_filename, 'rb') as input_file:
        event = ''
        cur_line = input_file.readline()
        cur_start_time = -1
        cur_end_time = -1
        under_another_event = False
        start_layout_ts = -1
        begin_counter = 0
        time_pairs = []
        timing_names = set()
        all_timings = defaultdict(lambda: 0)
        while cur_line != '':
            if 'Tracing.dataCollected' in cur_line and \
                event != '':
                # process the current event.
                try:
                    parsed_event = json.loads(event)
                except Exception as e:
                    event = ''
                    print 'Exception: ' + str(e)
                    continue
                params_values = parsed_event['params']['value']

                for val in params_values: # Iterate through each value.
                    timing_name = val['name']
                    timestamp = int(val['ts'])
                    event_type = val['ph']  # The type of the event
                    cat = val['cat']
                    if 'devtools.timeline' in cat and 'disabled-by-default-devtools.timeline' not in cat:
                        if timing_name == 'v8.parseOnBackground':
                            continue
                        if event_type == constants.TRACING_EVENT_BEGIN:
                            if (timestamp > cur_end_time and cur_end_time > -1) or \
                                (cur_start_time == -1):
                                cur_start_time = timestamp
                                cur_end_time = -1
                                # print val
                                # print str(cur_start_time) + ' ' + str(cur_end_time)
                                # print ''
                            begin_counter += 1
                        elif event_type == constants.TRACING_EVENT_END:
                            if begin_counter == 1 and \
                                timestamp > cur_end_time:
                                cur_end_time = timestamp
                                time_tuple = ( cur_start_time, cur_end_time )
                                time_pairs.append(time_tuple)
                                # print val
                                # print str(cur_start_time) + ' ' + str(cur_end_time)
                                # print ''
                                all_timings[timing_name] += cur_end_time - cur_start_time
                            begin_counter -= 1
                        elif event_type == constants.TRACING_EVENT_COMPLETE and \
                            begin_counter == 0: # Not a subevent.
                            if timestamp > cur_end_time:
                                cur_start_time = timestamp
                                if 'dur' in val:
                                    cur_end_time = timestamp + int(val['dur'])
                                    time_tuple = ( cur_start_time, cur_end_time )
                                    time_pairs.append(time_tuple)
                                    # print val
                                    # print str(cur_start_time) + ' ' + str(cur_end_time)
                                    # print ''
                                    all_timings[timing_name] += cur_end_time - cur_start_time

                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()
        # for t in timing_names:
        #     print t
        # print all_timings
        return time_pairs, all_timings

def check_times(time_pairs):
    prev_end_time = time_pairs[0][1]
    for i in range(1, len(time_pairs)):
        if prev_end_time > time_pairs[i][0]:
            print 'Ordering violated!'
            break
        prev_end_time = time_pairs[i][1]

def print_times(timing_types, aggregated_timings):
    output_line = ''
    for t in timing_types:
        output_line += ' ' + str(aggregated_timings[t])
    print output_line

def filter_keys(keys, original):
    return { key: value for key, value in original.iteritems() if key in keys }
    

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    for p in os.listdir(args.root_dir):
        tracing_filename = os.path.join(args.root_dir, p, 'tracing_' + p)
        if not os.path.exists(tracing_filename):
            continue
        time_pairs, aggregated_timings = parse_trace_file(tracing_filename)
        # check_times(time_pairs)
        timing_types = [ 'XHRReadyStateChange', 'Layout', 'XHRLoad', 'MajorGC', 'MinorGC', 'TimerFire', 'TimerFire', 'FunctionCall' ]
        filtered = filter_keys(timing_types, aggregated_timings)
        filtered['page'] = p
        print json.dumps(filtered)
