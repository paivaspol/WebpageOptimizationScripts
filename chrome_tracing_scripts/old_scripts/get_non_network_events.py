import simplejson as json

from argparse import ArgumentParser

RESOURCE_RECEIVED_DATA = 'ResourceReceivedData'
RESOURCE_FINISH = 'ResourceFinish'
RESOURCE_RECEIVED_RESPONSE = 'ResourceReceiveResponse'
RESOURCE_SEND_REQUEST = 'ResourceSendRequest'

def display_network_events(json_objs):
    start_time = find_lowest_timestamp(json_objs)
    for timeline_event in json_objs:
        if timeline_event['name'] == RESOURCE_RECEIVED_DATA or \
            timeline_event['name'] == RESOURCE_FINISH or \
            timeline_event['name'] == RESOURCE_RECEIVED_RESPONSE or \
            timeline_event['name'] == RESOURCE_SEND_REQUEST:
            a = 1
        else:
            # Non-networking events.
            if timeline_event['ph'] == 'X' and timeline_event['name'] != 'GPUTask':
                end_time = timeline_event['ts'] + timeline_event['dur']
                relative_start_time = to_ms(timeline_event['ts'] - start_time)
                relative_end_time = to_ms(end_time - start_time)
                print '0.75 {0} {2} {1}'.format(relative_start_time, timeline_event['name'], relative_end_time)

def get_timeline_objects(timeline_filename):
    with open(timeline_filename, 'rb') as input_file:
        json_str = ''
        for raw_line in input_file:
            json_str = json_str + raw_line.strip()
        result = json.loads(json_str)
        return result

def find_lowest_timestamp(timeline_objects):
    '''
    Finds the lowest timestamp.
    '''
    lowest_timestamp = None
    for timeline_object in timeline_objects:
        if lowest_timestamp is None and timeline_object['ts'] > 0:
            lowest_timestamp = timeline_object['ts']
            event = timeline_object
        elif lowest_timestamp is not None and timeline_object['ts'] > 0 and lowest_timestamp > timeline_object['ts']:
            lowest_timestamp = timeline_object['ts']
    return lowest_timestamp

def to_ms(microsecond_time):
    return 1.0 * microsecond_time / 1000

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('timeline_filename')
    args = parser.parse_args()
    timeline_objects = get_timeline_objects(args.timeline_filename)
    display_network_events(timeline_objects)
    
