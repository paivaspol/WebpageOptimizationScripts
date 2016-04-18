def extract_url_from_path(path, escape_path=False):
    '''
    Extracts the url from the path.
    '''
    if path.endswith('/'):
        path = path[:len(path) - 1]
    last_delim_index = -1
    for i in range(0, len(path)):
        if path[i] == '/':
            last_delim_index = i
    url = path[last_delim_index + 1:]
    if escape_path:
        url = url.replace('/', '_')
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
