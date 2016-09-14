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

def get_page_list(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        return [ line.strip() for line in input_file if not line.startswith('#') ]

def get_page_to_time_mapping(page_to_time_mapping_filename):
    with open(page_to_time_mapping_filename, 'rb') as input_file:
        result = [ x.strip().split() for x in input_file ]
        return { key: value for key, value in result }

