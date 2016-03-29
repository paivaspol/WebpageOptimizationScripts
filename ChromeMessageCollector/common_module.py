HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'

def escape_url(url):
    '''
    Escapes the URL using the following rules:
    1. If the URL ends with '/', remove it
    2. Remove 'http://' and 'www.' prefixes from the URL.
    3. Replace all occurences of '/' with '_'
    '''
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')
