import tldextract
import os

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

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory
