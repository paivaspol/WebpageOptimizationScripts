from urlparse import urlparse

import tldextract
import os
import simplejson as json

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

def parse_pages_file(pages_filename):
    pages = []
    with open(pages_filename, 'rb') as input_file:
        for raw_line in input_file:
            pages.append(raw_line.strip())
    return pages

def extract_domain(url):
    parsed_uri = tldextract.extract(url)
    return parsed_uri.domain + '.' + parsed_uri.suffix

def extract_domain_with_subdomain(url):
    parsed_uri = tldextract.extract(url)
    return parsed_uri.subdomain + '.' + parsed_uri.domain + '.' + parsed_uri.suffix

def extract_domain(url):
    parsed_uri = tldextract.extract(url)
    return parsed_uri.domain + '.' + parsed_uri.suffix

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory

def remove_file_if_exists(filename):
    if os.path.exists(filename):
        os.remove(filename)

def remove_non_external_domain(domain, dict_to_remove, request_to_url):
    copy = dict(dict_to_remove)
    keys_to_remove = []
    for key in copy:
        request_id = key
        if request_id.endswith('.beautified'):
            request_id = key[: len(key) - len('.beautified')]
        url = request_to_url[request_id]
        if domain == extract_domain(url):
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del copy[key]
    return copy

def remove_external_domain(domain, dict_to_remove, request_to_url):
    copy = dict(dict_to_remove)
    keys_to_remove = []
    for key in copy:
        request_id = key
        if request_id.endswith('.beautified'):
            request_id = key[: len(key) - len('.beautified')]
        url = request_to_url[request_id]
        if domain != extract_domain(url):
            keys_to_remove.append(key)
    for key in keys_to_remove:
        del copy[key]
    return copy

def get_css_children_count_dict(children_count_filename):
    result = dict()
    with open(children_count_filename, 'rb') as input_file:
        for raw_line in input_file:
            if raw_line.startswith('#'):
                continue
            line = raw_line.strip().split()
            # page -> (union, before_load, after_load, diff)
            result[line[0]] = (int(line[1]), int(line[2]), int(line[3]), int(line[4]))
    return result

def parse_request_to_url(request_to_url_filename):
    result = dict()
    with open(request_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = line[1]
    return result

def get_pages_without_pages_to_ignore(base_pages, pages_to_ignore_filename):
    pages_to_ignore = set()
    with open(pages_to_ignore_filename, 'rb') as input_file:
        for raw_line in input_file:
            pages_to_ignore.add(raw_line.strip())
    base_pages_set = set(base_pages)
    return base_pages_set - pages_to_ignore

def parse_page_id_to_domain_mapping(page_to_domain_mapping_filename):
    result = dict()
    with open(page_to_domain_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[1]] = line[0]
    return result

PARAMS = 'params'
METHOD = 'method'
REQUEST = 'request'

# Javascript Constants
INITIATOR = 'initiator'
TYPE = 'type'
SCRIPT = 'script'
STACK_TRACE = 'stackTrace'
URL = 'url'

def process_network_file(network_filename, page):
    children_from_js = set()
    same_domain_js = set()
    external_domain_js = set()
    seen_in_will_be_sent = set()
    all_requests = set()
    request_id_to_url_map = dict()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if not found_first_request and \
                network_event[METHOD] == 'Network.requestWillBeSent':
                if escape_page(network_event[PARAMS][REQUEST]['url']) \
                    == page:
                    found_first_request = True
            if not found_first_request:
                continue
            if network_event[METHOD] == 'Network.requestWillBeSent':
                seen_in_will_be_sent.add(network_event[PARAMS]['requestId'])
                if INITIATOR in network_event[PARAMS] and \
                    network_event[PARAMS][INITIATOR][TYPE] == SCRIPT and \
                    STACK_TRACE in network_event[PARAMS][INITIATOR]:
                    stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                    if len(stack_trace) > 0:
                        url = stack_trace[0][URL]
                        parsed_url = urlparse(url)
                        if '.js?' in parsed_url.path or parsed_url.path.endswith('.js'):
                            request_id = network_event[PARAMS]['requestId']
                            if extract_domain(url) != page:
                                external_domain_js.add(request_id)
                            else:
                                same_domain_js.add(request_id)
                            children_from_js.add(request_id)
            elif network_event[METHOD] == 'Network.responseReceived':
                request_id = network_event[PARAMS]['requestId']
                all_requests.add(request_id)
                request_id_to_url_map[request_id] = network_event[PARAMS]['response']['url']
    all_requests = all_requests & seen_in_will_be_sent
    real_children_from_js = children_from_js & all_requests
    same_domain_js = same_domain_js & all_requests
    external_domain_js = external_domain_js & all_requests
    return real_children_from_js, same_domain_js, external_domain_js, all_requests, request_id_to_url_map

def find_unique_children(network_filename, page):
    children_from_js = set()
    same_domain_js = set()
    external_domain_js = set()
    seen_in_will_be_sent = set()
    all_requests = set()
    request_id_to_url_map = dict()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            network_event = json.loads(json.loads(raw_line.strip()))
            if not found_first_request and \
                network_event[METHOD] == 'Network.requestWillBeSent':
                if escape_page(network_event[PARAMS][REQUEST]['url']) \
                    == page:
                    found_first_request = True
            if not found_first_request:
                continue
            if network_event[METHOD] == 'Network.requestWillBeSent':
                seen_in_will_be_sent.add(network_event[PARAMS]['request']['url'])
                if INITIATOR in network_event[PARAMS] and \
                    network_event[PARAMS][INITIATOR][TYPE] == SCRIPT and \
                    STACK_TRACE in network_event[PARAMS][INITIATOR]:
                    stack_trace = network_event[PARAMS][INITIATOR][STACK_TRACE]
                    if len(stack_trace) > 0:
                        url = stack_trace[0][URL]
                        parsed_url = urlparse(url)
                        if '.js?' in parsed_url.path or parsed_url.path.endswith('.js'):
                            request_id = network_event[PARAMS]['requestId']
                            if extract_domain(url) != page:
                                external_domain_js.add(network_event[PARAMS]['request']['url'])
                            else:
                                same_domain_js.add(network_event[PARAMS]['request']['url'])
                            children_from_js.add(network_event[PARAMS]['request']['url'])
            elif network_event[METHOD] == 'Network.responseReceived':
                request_id = network_event[PARAMS]['requestId']
                all_requests.add(network_event[PARAMS]['response']['url'])
                request_id_to_url_map[request_id] = network_event[PARAMS]['response']['url']
    all_requests = all_requests & seen_in_will_be_sent
    real_children_from_js = children_from_js & all_requests
    same_domain_js = same_domain_js & all_requests
    external_domain_js = external_domain_js & all_requests
    return real_children_from_js, same_domain_js, external_domain_js, all_requests, request_id_to_url_map
