from argparse import ArgumentParser

import common_module
import datetime
import os
import simplejson as json

METHOD = 'method'
PARAMS = 'params'
REQUEST_ID = 'requestId'
WALLTIME = 'wallTime'
TIMESTAMP = 'timestamp'
URL = 'url'
STATUS_TEXT = 'statusText'
STATUS = 'status'
PROTOCOL = 'protocol'

# timing keys
BLOCKED = 'blocked'
DNS = 'dns'
CONNECT = 'connect'
SEND = 'send'
WAIT = 'wait'
RECEIVE = 'receive'
SSL = 'ssl'
PAGEREF = 'pageref'
STARTED_DATE_TIME = 'startedDateTime'
TIME = 'time'
REQUEST = 'request'
RESPONSE = 'response'
CACHE = 'cache'
TIMINGS = 'timings'
SERVER_IP_ADDRESS = 'serverIPAddress'
INITIATOR = 'initiator'
HTTP_VERSION = 'httpVersion'
COOKIES = 'cookies'
HEADERS = 'headers'
QUERY_STRING = 'queryString'
HEADERS_SIZE = 'headersSize'
BODY_SIZE = 'bodySize'
STATUS = 'status'
STATUS_TEXT = 'statusText'
REDIRECT_URL = 'redirectURL'
TIMING = 'timing'
DNS_START = 'dnsStart'
CONNECT_START = 'connectStart'
SEND_START = 'sendStart'
SEND_END = 'sendEnd'
RECEIVE_HEADERS_END = 'receiveHeadersEnd'
SSL_END = 'sslEnd'
SSL_START = 'sslStart'
REMOTE_IP_ADDRESS = 'remoteIPAddress'
CONNECTION = 'connection'
CONNECTION_ID = 'connectionId'
CONTENT = 'content'
SIZE = 'size'
COMPRESSION = 'compression'
MIME_TYPE = 'mimeType'
TEXT = 'text'
ID = 'id'
TITLE = 'title'
PAGE_TIMINGS = 'pageTimings'

def main(root_dir, output_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        print 'Processing: ' + page
        process_page(root_dir, page, output_dir)

def process_page(root_dir, page, output_dir):
    network_filename = os.path.join(root_dir, page, 'network_' + page)
    if not os.path.exists(network_filename):
        return None
    har_object = dict()
    har_object['log'] = dict()
    har_object['log']['creator'] = dict()
    har_object['log']['creator']['name'] = 'Vaspol Ruamviboonsuk'
    har_object['log']['creator']['version'] = '3.14'
    har_object['log']['version'] = '1.2'
    har_object['log']['pages'] = []

    initial_walltime, entries = get_entries(network_filename, page)
    har_object['log']['entries'] = entries.values()

    page_object = dict()
    page_object[STARTED_DATE_TIME] = datetime.datetime.utcfromtimestamp(initial_walltime).isoformat() + 'Z'
    page_object[ID] = page
    page_object[TITLE] = page
    page_object[PAGE_TIMINGS] = dict()
    page_object[PAGE_TIMINGS]['onContentLoad'] = '-1'
    page_object[PAGE_TIMINGS]['onLoad'] = '-1'
    output_to_file(output_dir, page, har_object)

def output_to_file(output_dir, page, har_object):
    output_filename = os.path.join(output_dir, page + '.har')
    common_module.create_directory_if_not_exists(output_dir)
    with open(output_filename, 'wb') as output_file:
        json.dump(har_object, output_file)

def get_entries(network_filename, page):
    request_id_to_times = dict()
    request_id_to_entry = dict()
    request_id_to_timing_object = dict()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for line in input_file:
            network_event = json.loads(json.loads(line.strip()))
            if not found_first_request and \
                network_event[METHOD] == 'Network.requestWillBeSent':
                if common_module.escape_page(network_event[PARAMS][REQUEST]['url']) \
                    == page:
                    found_first_request = True
                    initial_walltime = network_event[PARAMS][WALLTIME]
            if not found_first_request:
                continue
            request_id = network_event[PARAMS][REQUEST_ID]
            if network_event[METHOD] == 'Network.requestWillBeSent':
                # Get the time.
                timestamp = network_event[PARAMS][TIMESTAMP]
                wall_time = network_event[PARAMS][WALLTIME]
                request_id_to_times[request_id] = (timestamp, wall_time)

                # Create entry object and populate the entry and the request part of the entry.
                request_id_to_entry[request_id] = generate_default_entry_object()
                entry = request_id_to_entry[request_id]
                entry[PAGEREF] = page
                entry[STARTED_DATE_TIME] = datetime.datetime.utcfromtimestamp(wall_time).isoformat() + 'Z'
                entry[REQUEST] = generate_request_object(network_event)
            elif network_event[METHOD] == 'Network.responseReceived':
                if request_id not in request_id_to_entry:
                    continue
                entry = request_id_to_entry[request_id]
                entry[RESPONSE] = generate_response_object(network_event)
                entry[REQUEST][HTTP_VERSION] = entry[RESPONSE][HTTP_VERSION]
                entry[SERVER_IP_ADDRESS] = network_event[PARAMS][RESPONSE][REMOTE_IP_ADDRESS] if REMOTE_IP_ADDRESS in network_event[PARAMS][RESPONSE] else ''
                entry[CONNECTION] = str(network_event[PARAMS][RESPONSE][CONNECTION_ID])
                request_id_to_timing_object[request_id] = network_event[PARAMS][RESPONSE][TIMING] if TIMING in network_event[PARAMS][RESPONSE] else None
            elif network_event[METHOD] == 'Network.loadingFinished':
                entry = request_id_to_entry[request_id]
                # print network_event[PARAMS][TIMESTAMP]
                # print request_id_to_times[request_id][0]
                load_time = network_event[PARAMS][TIMESTAMP] - request_id_to_times[request_id][0]
                entry[TIME] = to_millis(load_time)
                timing_object = request_id_to_timing_object[request_id]
                if timing_object is None:
                    del request_id_to_timing_object[request_id]
                    del request_id_to_entry[request_id]
                else:
                    entry[TIMINGS] = generate_timing_object(timing_object, load_time)
    return initial_walltime, request_id_to_entry

def generate_default_entry_object():
    default_entry_object = dict()
    default_entry_object[PAGEREF] = None
    default_entry_object[STARTED_DATE_TIME] = None
    default_entry_object[TIME] = -1
    default_entry_object[REQUEST] = None
    default_entry_object[RESPONSE] = None
    default_entry_object[CACHE] = dict()
    default_entry_object[TIMINGS] = None
    default_entry_object[SERVER_IP_ADDRESS] = ''
    default_entry_object[CONNECTION] = ''
    default_entry_object[INITIATOR] = None
    return default_entry_object

def generate_request_object(request_network_event):
    request_object = dict()
    request_object[METHOD] = request_network_event[PARAMS][REQUEST][METHOD]
    request_object[URL] = request_network_event[PARAMS][REQUEST][URL]
    request_object[HTTP_VERSION] = ''
    request_object[COOKIES] = []
    request_object[HEADERS] = []
    request_object[QUERY_STRING] = []
    request_object[HEADERS_SIZE] = -1 # Default placeholder
    request_object[BODY_SIZE] = -1 # Default placeholder
    return request_object

def generate_response_object(response_network_event):
    # print response_network_event
    response_object = dict()
    response_object[STATUS] = response_network_event[PARAMS][RESPONSE][STATUS]
    response_object[STATUS_TEXT] = response_network_event[PARAMS][RESPONSE][STATUS_TEXT]
    response_object[HTTP_VERSION] = response_network_event[PARAMS][RESPONSE][PROTOCOL]
    response_object[COOKIES] = []
    response_object[HEADERS] = []
    response_object[REDIRECT_URL] = ''
    response_object[HEADERS_SIZE] = -1
    response_object[BODY_SIZE] = -1
    response_object[CONTENT] = dict()
    response_object[CONTENT][SIZE] = '0'
    response_object[CONTENT][COMPRESSION] = '0'
    response_object[CONTENT][MIME_TYPE] = ''
    response_object[CONTENT][TEXT] = ''
    return response_object

def generate_timing_object(timing_object, duration):
    default_timing_object = dict()
    default_timing_object[BLOCKED] = first_non_negative([timing_object[DNS_START], timing_object[CONNECT_START], timing_object[SEND_START]])
    default_timing_object[DNS] = -1
    if timing_object[DNS_START] >= 0:
        default_timing_object[DNS] = first_non_negative([timing_object[CONNECT_START], timing_object[SEND_START]]) - timing_object[DNS_START]

    default_timing_object[CONNECT] = -1
    if timing_object[CONNECT_START] >= 0:
        default_timing_object[CONNECT] = timing_object[SEND_START] - timing_object[CONNECT_START]
    default_timing_object[SEND] = timing_object[SEND_END] - timing_object[SEND_START]
    default_timing_object[WAIT] = timing_object[RECEIVE_HEADERS_END] - timing_object[SEND_END]
    default_timing_object[RECEIVE] = to_millis(duration) - timing_object[RECEIVE_HEADERS_END]
    default_timing_object[SSL] = -1
    if timing_object[SSL_END] >= 0 and timing_object[SSL_START] >= 0:
        default_timing_object[SSL] = timing_object[SSL_END] - timing_object[SSL_START]
    return default_timing_object

def first_non_negative(values):
    for value in values:
        if value >= 0:
            return value
    return -1

def to_millis(time):
    return -1 if time == -1 else time * 1000

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)

