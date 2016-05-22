import simplejson as json

def parse_page_start_end_time(page_start_end_time_filename):
    '''
    Parses the page start and end time and returns a list of tuples in the following format:
        ('page', ([start], [end]))
    '''
    result = []
    with open(page_start_end_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.append((line[0], (float(line[1]), float(line[2]))))
    if len(result) > 1:
        return result
    else:
        return result[0]

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

def convert_to_mbits(byte):
    return byte * 8e-6

def compute_utilization(bytes_received, bandwidth=6, interval=100):
    '''
    bandwidth is in mbps
    Interval is in MS
    '''
    return convert_to_mbits(bytes_received) / (interval * bandwidth / 1000.0)

def check_web_port(use_spdyproxy, tcp_port):
    if use_spdyproxy:
        return tcp_port == 44300 or tcp_port == 3000
    else:
        return tcp_port == 443 or tcp_port == 80

# Returns a list of objectified network events.
def parse_network_events(network_events_filename):
    result = []
    with open(network_events_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if network_event['method'] != 'Network.requestServedFromCache':
                result.append(network_event)
    return result

def parse_pages_to_use(pages_to_use_filename):
    result = set()
    if pages_to_use_filename is None:
        return result
    with open(pages_to_use_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.add(line[0])
    return result

def parse_requests_to_ignore(requests_to_ignore_filename):
    result = dict()
    with open(requests_to_ignore_filename, 'rb') as input_file:
        current_url = ''
        for raw_line in input_file:
            if raw_line.startswith('page'):
                line = raw_line.strip().split()
                result[line[1]] = []
                current_url = line[1]
            else:
                result[current_url].append(raw_line.strip())
    return result

def parse_requests_to_ignore_in_url_directory(requests_to_ignore_filename):
    result = set()
    with open(requests_to_ignore_filename, 'rb') as input_file:
        for raw_line in input_file:
            result.add(raw_line.strip())
    return result
