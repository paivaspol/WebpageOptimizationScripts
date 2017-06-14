from argparse import ArgumentParser
from collections import defaultdict

import constants
import json
import os
import sys

def parse_trace_file(tracing_filename):
    with open(tracing_filename, 'rb') as input_file:
        event = ''
        cur_line = input_file.readline()
        cur_start_time = -1
        cur_end_time = -1
        under_another_event = False
        start_layout_ts = -1
        begin_counter = 0
        time_pairs_dict = defaultdict(list)
        timing_names = set()
        all_timings = defaultdict(lambda: 0)
        first_req_time = -1
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
                                if cur_end_time > -1:
                                    all_timings['idle'] += timestamp - cur_end_time
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
                                time_pairs_dict[timing_name].append(time_tuple)
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
                                    if cur_end_time > -1:
                                        all_timings['idle'] += timestamp - cur_end_time
                                    cur_end_time = timestamp + int(val['dur'])
                                    time_tuple = ( cur_start_time, cur_end_time )
                                    time_pairs_dict[timing_name].append(time_tuple)
                                    # print val
                                    # print str(cur_start_time) + ' ' + str(cur_end_time)
                                    # print ''
                                    all_timings[timing_name] += cur_end_time - cur_start_time
                        elif event_type == constants.TRACING_EVENT_INSTANT:
                            if timing_name == constants.TRACING_NETWORK_RESOURCE_SEND_REQUEST and \
                                first_req_time == -1:
                                first_req_time = timestamp
                                print val
                                print str(cur_start_time) + ' ' + str(cur_end_time)
                                print ''

                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()
        return time_pairs_dict, all_timings, first_req_time

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

def filter_keys(keys, original, exclude=False):
    if exclude:
        return { key: value for key, value in original.iteritems() if key not in keys }
    else:
        return { key: value for key, value in original.iteritems() if key in keys }

def get_network_timings_hinted_not_preloaded(timing_filename, first_req_time, dependencies):
    result = dict()
    with open(timing_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip()
            timing = json.loads(l)
            url = timing['url']
            if not timing[constants.TRACING_PRELOADED] and url in dependencies:
                send_request = timing['ResourceSendRequest'] + first_req_time
                discovery_time = timing['discovery_time'] + first_req_time
                preload_discovery_time = timing['ResourcePreloadDiscovery'] + first_req_time
                finish_time = timing['ResourceFinish'] + first_req_time
                first_byte_time = timing['ResourceReceiveResponse'] + first_req_time
                url = timing['url']
                result[url] = [ send_request, discovery_time, preload_discovery_time, first_byte_time, finish_time ]
    return result

def get_network_timings(timing_filename, first_req_time):
    result = dict()
    with open(timing_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip()
            timing = json.loads(l)
            if timing[constants.TRACING_PRELOADED]:
                send_request = timing['ResourceSendRequest'] + first_req_time
                discovery_time = timing['discovery_time'] + first_req_time
                preload_discovery_time = timing['ResourcePreloadDiscovery'] + first_req_time
                finish_time = timing['ResourceFinish'] + first_req_time
                first_byte_time = timing['ResourceReceiveResponse'] + first_req_time
                url = timing['url']
                result[url] = [ send_request, discovery_time, preload_discovery_time, first_byte_time, finish_time ]
    return result

def get_network_timings_unhinted_resources(timing_filename, first_req_time, dependencies):
    result = dict()
    with open(timing_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip()
            timing = json.loads(l)
            if timing['url'] not in dependencies:
                send_request = timing['ResourceSendRequest'] + first_req_time
                discovery_time = timing['discovery_time'] + first_req_time
                preload_discovery_time = timing['ResourcePreloadDiscovery'] + first_req_time
                finish_time = timing['ResourceFinish'] + first_req_time
                first_byte_time = timing['ResourceReceiveResponse'] + first_req_time
                url = timing['url']
                result[url] = [ send_request, discovery_time, preload_discovery_time, first_byte_time, finish_time ]
    return result

def construct_timing_pair_list(keys, original, exclude=False):
    result = []
    if exclude:
        for key in original:
            if key not in keys:
                result.extend([ (key, x) for x in original[key] ])
    else:
        for key in original:
            if key in keys:
                result.extend([ (key, x) for x in original[key] ])
    return sorted(result, key=lambda x: x[1][0])

def get_actual_network_wait_time(network_timings, timings_on_main_process):
    result = dict()
    for url in network_timings:
        discovery_time = network_timings[url][1]
        finish_time = network_timings[url][4]
        remove = 0
        for key, t in timings_on_main_process:
            if discovery_time < t[0] < t[1] < finish_time:
                remove += t[1] - t[0]
                # if 'foundation-icon' in url:
                #     print key + ' ' + str(t[1] - t[0]) + ' ' + str(remove)
            elif t[0] < discovery_time < t[1]: # Discovery in the middle of another event.
                remove += t[1] - discovery_time
        real_wait_time = (finish_time - discovery_time) - remove
        result[url] = (discovery_time, max(0, real_wait_time))
    return result

def get_actual_first_byte_time(network_timings, timings_on_main_process):
    result = dict()
    for url in network_timings:
        discovery_time = network_timings[url][1]
        first_byte_time = network_timings[url][3]
        remove = 0
        for key, t in timings_on_main_process:
            if discovery_time < t[0] < t[1] < first_byte_time:
                remove += t[1] - t[0]
                # if 'foundation-icon' in url:
                #     print key + ' ' + str(t[1] - t[0]) + ' ' + str(remove)
            elif t[0] < discovery_time < t[1]: # Discovery in the middle of another event.
                remove += t[1] - discovery_time
        real_wait_time = (first_byte_time - discovery_time) - remove
        result[url] = (discovery_time, max(0, real_wait_time))
    return result

def output_to_file(actual_network_wait_time, output_dir, first_req_time):
    with open(os.path.join(output_dir, p), 'wb') as output_file:
        sorted_actual_network_wait_time = sorted(actual_network_wait_time.iteritems(), key=lambda x: x[0][1])
        for url, times in sorted_actual_network_wait_time:
            discovery_time = times[0] - first_req_time
            wait_time = times[1]
            output_file.write('{0}\t{1}\t{2}\n'.format(url, discovery_time, wait_time))

def get_dependencies(dependency_filename):
    result = []
    cat_to_deps = defaultdict(list)
    with open(dependency_filename, 'rb') as input_file:
        for l in input_file:
            l = l.strip().split()
            result.append(l[2])
            cat_to_deps[l[-1]].append(l[2])
    return result, cat_to_deps

def get_invocation_time(cat_to_deps, cat, timings):
    urls = cat_to_deps[cat]
    retval = sys.maxint
    for url in timings:
        if url in urls:
            retval = min(retval, timings[url][0])
    if retval == sys.maxint:
        retval = -1
    return retval

def get_last_byte_time(cat_to_deps, cat, timings):
    urls = cat_to_deps[cat]
    retval = -1
    for url in timings:
        if url in urls:
            retval = max(retval, timings[url][-1])
    return retval

def output_invocation(output_filename, result):
    with open(output_filename, 'wb') as output_file:
        for l in result:
            output_file.write(l + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('extended_waterfall_json_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)
    invocations = []
    for p in os.listdir(args.root_dir):
        # if 'mobile.nytimes.com' not in p:
        #     continue
        tracing_filename = os.path.join(args.root_dir, p, 'tracing_' + p)
        timing_filename = os.path.join(args.extended_waterfall_json_dir, p, 'timings.txt')
        dependency_filename = os.path.join(args.dependency_dir, p, 'dependency_tree.txt')
        if not (os.path.exists(tracing_filename) and os.path.exists(timing_filename) and os.path.exists(dependency_filename)):
            continue
        hinted_and_preloaded_output_dir = os.path.join(args.output_dir, 'hinted_and_preloaded')
        hinted_and_not_preloaded_output_dir = os.path.join(args.output_dir, 'hinted_but_not_preloaded')
        first_byte_time_dir = os.path.join(args.output_dir, 'hinted_and_preloaded_first_byte_time')
        unhinted_output_dir = os.path.join(args.output_dir, 'not_hinted')
        if not os.path.exists(hinted_and_preloaded_output_dir):
            os.mkdir(hinted_and_preloaded_output_dir)
            os.mkdir(hinted_and_not_preloaded_output_dir)
            os.mkdir(first_byte_time_dir)
            os.mkdir(unhinted_output_dir)

        time_pairs, aggregated_timings, first_req_time = parse_trace_file(tracing_filename)
        network_timings = get_network_timings(timing_filename, first_req_time)
        # excluding_types = [ 'EvaluateScript', 'ParseHTML', 'ParseAuthorStyleSheet', 'idle' ]
        excluding_types = [ ]
        timing_pair_list = construct_timing_pair_list(excluding_types, time_pairs, exclude=True)
        actual_wait_time = get_actual_network_wait_time(network_timings, timing_pair_list)
        output_to_file(actual_wait_time, hinted_and_preloaded_output_dir, first_req_time)

        actual_wait_time = get_actual_first_byte_time(network_timings, timing_pair_list)
        output_to_file(actual_wait_time, first_byte_time_dir, first_req_time)

        dependencies, cat_to_deps = get_dependencies(dependency_filename)
        network_timings_hinted_but_not_preloaded = get_network_timings_hinted_not_preloaded(timing_filename, first_req_time, dependencies)
        actual_wait_time = get_actual_network_wait_time(network_timings_hinted_but_not_preloaded, timing_pair_list)
        output_to_file(actual_wait_time, hinted_and_not_preloaded_output_dir, first_req_time)

        network_timings_unhinted_resources = get_network_timings_unhinted_resources(timing_filename, first_req_time, dependencies)
        actual_wait_time = get_actual_network_wait_time(network_timings_unhinted_resources, timing_pair_list)
        output_to_file(actual_wait_time, unhinted_output_dir, first_req_time)

        important_invocation = get_invocation_time(cat_to_deps, 'Important', network_timings) - first_req_time
        semi_important_invocation = get_invocation_time(cat_to_deps, 'Semi-important', network_timings) - first_req_time
        unimportant_invocation = get_invocation_time(cat_to_deps, 'Unimportant', network_timings) - first_req_time
        if semi_important_invocation == -1:
            semi_important_invocation = get_last_byte_time(cat_to_deps, 'Important', network_timings) - first_req_time
        if unimportant_invocation == -1:
            unimportant_invocation = get_last_byte_time(cat_to_deps, 'Semi-important', network_timings) - first_req_time
        output_line = '{0} {1} {2} {3}'.format(p, important_invocation, semi_important_invocation, unimportant_invocation)
        invocations.append(output_line)
    output_invocation(os.path.join(args.output_dir, 'scheduler_execution_time'), invocations)
