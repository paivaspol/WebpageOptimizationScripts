import simplejson as json

PARAMS = 'params'

def parse_network_file(chrome_network_file):
    '''
    Parsers the chrome network events.
    Returns a dictionary mapping: request id -> (requestWillBeSent, loadingFinished)
    '''
    result = dict() # Mapping: request id --> (requestWillBeSent, loadingFinished)
    walltime_dict = dict()
    timestamp_dict = dict() # Mapping: request id --> timestamp
    with open(chrome_network_file, 'rb') as input_file:
        for raw_line in input_file:
            event = json.loads(json.loads(raw_line.strip()))
            if event['method'] == 'Network.requestWillBeSent':
                request_id, timestamp = get_requestid_and_timestamp(event)
                wallTime = convert_to_ms_precision(float(event[PARAMS]['wallTime']))
                walltime_dict[request_id] = wallTime
                timestamp_dict[request_id] = timestamp
            elif (event['method'] == 'Network.loadingFinished' or \
                event['method'] == 'Network.loadingFailed'):
                request_id, timestamp = get_requestid_and_timestamp(event)
                if request_id in walltime_dict and request_id in timestamp_dict:
                    current_wallTime = walltime_dict[request_id] + (timestamp - timestamp_dict[request_id])
                    result[request_id] = (walltime_dict[request_id], current_wallTime)
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

def extract_url_from_path(path):
    '''
    Extracts the url from the path.
    '''
    if path.endswith('/'):
        path = path[:len(path) - 1]
    last_delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            last_delim_index = i
    url = path[last_delim_index + 1:].replace('/', '_')
    return url

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


def parse_pages_to_ignore(pages_to_ignore_filename):
    pages = set()
    if pages_to_ignore_filename is not None:
        with open(pages_to_ignore_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip()
                pages.add(escape_page(line))
    print pages
    return pages

