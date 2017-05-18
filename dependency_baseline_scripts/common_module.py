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

def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ escape_page(line[len(line) - 1]) for line in temp ]

def get_pages_with_redirection(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ (escape_page(line[0]), escape_page(line[len(line) - 1])) for line in temp ]

def extract_url_from_link_string(link_string):
    # First, split by space.
    result_urls = set()
    splitted_link_string = link_string.split(' ')
    for link_token in splitted_link_string:
        splitted_link_token = link_token.split(';')
        if len(splitted_link_token) >= 3:
            url = splitted_link_token[0]
            rel = splitted_link_token[1]
            try:
                _, rel_type = rel.split('=')
                if rel_type == 'preload':
                    result_urls.add(url[1:len(url) - 1]) # Remove < and > at the beginning and end of string
            except Exception as e:
                pass
                
    return result_urls

def get_dependencies(dependency_filename, use_only_important_resources):
    results = []
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            resource_type = line[4]
            if use_only_important_resources and (line[6] != "Important"):
                continue
            results.append(line[2])
    return results

def get_dependencies_without_other_iframes(dependency_filename, use_only_important_resources, page):
    results = []
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = escape_page(line[0])
            resource_type = line[4]
            if (use_only_important_resources \
                and not (resource_type == 'Document' or resource_type == 'Script' or resource_type == 'Stylesheet')) \
                or (url != page) \
                or (resource_type == 'Document'):
                continue
            results.append(line[2])
    return results

def get_unimportant_dependencies(dependency_filename):
    results = []
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            resource_type = line[4]
            if not (resource_type == 'Document' or resource_type == 'Script' or resource_type == 'Stylesheet'):
                results.append(line[2])
    return results

def get_page_to_run_index(page_to_run_index):
    with open(page_to_run_index, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return { key: int(value) for key, value in temp }

import constants

def is_request_from_scheduler(initiator_obj, page, request_type):
    initiator_type = initiator_obj[constants.TYPE]
    if initiator_type != 'script':
        return False

    callframes = initiator_obj['stack']['callFrames']
    if len(callframes) != 1:
        return False
    url = callframes[0][constants.URL]
    function_name = callframes[0]['functionName']
    return request_type == 'XHR' \
            and escape_page(url) == page \
            and (function_name == 'important_url_handler' \
                 or len(function_name) == 0 \
                 or function_name == 'nrWrapper')
