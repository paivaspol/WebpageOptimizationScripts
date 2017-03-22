import simplejson as json
import os

PARAMS = 'params'

def get_preloaded_timings(timing_filename):
    url_to_timing = {}
    with open(timing_filename, 'rb') as input_file:
        for raw_line in input_file:
            timing = json.loads(raw_line.strip())
            url_to_timing[timing['url']] = timing

    result = []
    for url, timing in url_to_timing.iteritems():
        if timing['preloaded']:
            # print timing
            # Wait time is define max(0, discovery - resource finish)
            # print 'url: ' + url + ' discovery_time: ' + str(timing['discovery_time']) + ' finish: ' + str(timing['ResourceFinish'])
            send_request = timing['ResourceSendRequest']
            discovery_time = timing['discovery_time']
            preload_discovery_time = timing['ResourcePreloadDiscovery']
            net_wait_time = max(0, timing['ResourceFinish'] - timing['discovery_time'] )
            result.append( (url, discovery_time, net_wait_time, preload_discovery_time) )

    sorted_result = sorted(result, key=lambda x: x[1])
    return sorted_result

def get_requestid_and_timestamp(event):
    '''
    Extracts the request id and the timestamp from the event.
    '''
    requestId = event[PARAMS]['requestId']
    timestamp = convert_to_ms_precision(float(event[PARAMS]['timestamp']))
    return requestId, timestamp

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory

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
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'
def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
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

def parse_page_start_end_time(filename):
    with open(filename, 'rb') as input_file:
        line = input_file.readline().strip().split()
        web_perf_nav_start = float(line[1])
        web_perf_load_event = float(line[2])
        chrome_ts_nav_start = float(line[3])
        chrome_ts_load_event = float(line[4])
        return (line[0], (web_perf_nav_start, web_perf_load_event), (chrome_ts_nav_start, chrome_ts_load_event))

def convert_to_ms(time_in_seconds):
    return time_in_seconds * 1000

def get_pages_without_pages_to_ignore(base_pages, pages_to_ignore_filename):
    pages_to_ignore = set()
    with open(pages_to_ignore_filename, 'rb') as input_file:
        for raw_line in input_file:
            pages_to_ignore.add(raw_line.strip())
    base_pages_set = set(base_pages)
    return base_pages_set - pages_to_ignore

def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ escape_page(line[len(line) - 1]) for line in temp ]

def get_pages_with_redirection(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ (escape_page(line[0]), escape_page(line[len(line) - 1])) for line in temp if not line[0].startswith('#') ]

def remove_json(filename):
    if filename.endswith('.json'):
        return filename[:len(filename) - len('.json')]
    return filename
