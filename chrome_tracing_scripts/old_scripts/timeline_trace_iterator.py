import simplejson as json

from argparse import ArgumentParser

def iterate_through_timeline_events(timeline_objects):
    lowest_timestamp = None
    event = None
    beforeunload_event = None
    for timeline_object in timeline_objects:
        if lowest_timestamp is None and timeline_object['ts'] > 0:
            lowest_timestamp = timeline_object['ts']
            event = timeline_object
        elif lowest_timestamp is not None and timeline_object['ts'] > 0 and lowest_timestamp > timeline_object['ts']:
            lowest_timestamp = timeline_object['ts']
            event = timeline_object
         # elif timeline_object['name'] == 'EventDispatch' and timeline_object['args']['data']['type'] == 'beforeunload':

        if timeline_object['name'] == 'EventDispatch' and timeline_object['args']['data']['type'] == 'beforeunload':
            beforeunload_event = timeline_object

    print 'Lowest timestamp: {0}; event: {1}; before_unload_event: {2}'.format(lowest_timestamp, event, beforeunload_event)

def get_timeline_objects(timeline_filename):
    with open(timeline_filename, 'rb') as input_file:
        json_str = ''
        for raw_line in input_file:
            json_str = json_str + raw_line.strip()
        result = json.loads(json_str)
        return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('timeline_filename')
    args = parser.parse_args()
    timeline_objects = get_timeline_objects(args.timeline_filename)
    iterate_through_timeline_events(timeline_objects)

