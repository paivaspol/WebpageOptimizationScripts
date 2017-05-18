from argparse import ArgumentParser

import constants
import json

def parse_trace_file(tracing_filename):
    with open(tracing_filename, 'rb') as input_file:
        event = ''
        cur_line = input_file.readline()
        timer_fire_time = 0
        event_dispatch_time = 0
        xhr_ready_state_change_time = 0
        layout_time = 0
        counter = 0
        events = set()
        under_another_event = False
        start_layout_ts = -1
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
                    if cat == 'devtools.timeline':
                        events.add(timing_name)

                    if event_type == constants.TRACING_EVENT_BEGIN and timing_name != constants.TRACING_LAYOUT:
                        under_another_event = True
                    elif event_type == constants.TRACING_EVENT_END and timing_name != constants.TRACING_LAYOUT:
                        under_another_event = False

                    if not under_another_event:
                        if timing_name == constants.TRACING_SCRIPT_TIMER_FIRE:
                            if 'dur' in val:
                                timer_id = int(val['args']['data']['timerId'])
                                timer_fire_time += int(val['dur'])
                        elif timing_name == constants.TRACING_SCRIPT_EVENT_DISPATCH:
                            event_dispatch_time += int(val['dur'])
                        elif timing_name == constants.TRACING_SCRIPT_XHR_READY_STATE_CHANGE:
                            xhr_ready_state_change_time += int(val['dur'])
                        elif timing_name == constants.TRACING_LAYOUT:
                            if start_layout_ts == -1 and event_type == constants.TRACING_EVENT_BEGIN:
                                start_layout_ts = timestamp
                            elif start_layout_ts >= 0 and event_type == constants.TRACING_EVENT_END:
                                layout_time += timestamp - start_layout_ts
                                start_layout_ts = -1 # reset start_layout_ts

                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()
    for e in events:
        print e
    return timer_fire_time, event_dispatch_time, xhr_ready_state_change_time, layout_time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('tracing_filename')
    args = parser.parse_args()
    timer_fire_time, event_dispatch_time, xhr_ready_state_change_time, layout_time = parse_trace_file(args.tracing_filename)
    print '{0} {1} {2} {3}'.format(timer_fire_time, event_dispatch_time, xhr_ready_state_change_time, layout_time)
