import simplejson as json

PARAMS = 'params'

def parse_network_file(chrome_network_file):
    '''
    Parsers the chrome network events.
    Returns a dictionary mapping: request id -> (requestWillBeSent, loadingFinished)
    '''
    result = dict() # Mapping: request id --> (requestWillBeSent, loadingFinished)
    timestamp_dict = dict() # Mapping: request id --> timestamp
    with open(chrome_network_file, 'rb') as input_file:
        for raw_line in input_file:
            event = json.loads(json.loads(raw_line.strip()))
            if event['method'] == 'Network.requestWillBeSent':
                request_id, timestamp = get_requestid_and_timestamp(event)
                wallTime = convert_to_ms_precision(float(event[PARAMS]['wallTime']))
                result[request_id] = (wallTime, -1)
                timestamp_dict[request_id] = timestamp
            elif event['method'] == 'Network.loadingFinished' or \
                event['method'] == 'Network.loadingFailed':
                request_id, timestamp = get_requestid_and_timestamp(event)
                if request_id in result:
                    current_wallTime = result[request_id][0] + (timestamp - timestamp_dict[request_id])
                    result[request_id] = (result[request_id][0], current_wallTime)
    sorted_result = sorted(result.iteritems(), key=lambda x: x[1][0])

    return sorted_result

def get_requestid_and_timestamp(event):
    '''
    Extracts the request id and the timestamp from the event.
    '''
    requestId = event[PARAMS]['requestId']
    timestamp = convert_to_ms_precision(float(event[PARAMS]['timestamp']))
    return requestId, timestamp

def convert_to_ms_precision(timestamp):
    '''
    Converts the timestamp to millisecond precision.
    '''
    return timestamp * 1000

def parse_utilization_file(utilization_filename):
    '''
    Parses the utilizations file and return a list containing tuples of intervals and utilization.
    The list is sorted on the start of the interval.
    '''
    result = dict()
    with open(utilization_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            key = float(line[2]), float(line[3])
            value = float(line[1])
            result[key] = value
    return sorted(result.iteritems(), key=lambda x: x[0][0])

