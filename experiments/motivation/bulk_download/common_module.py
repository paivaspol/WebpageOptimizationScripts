def generate_content(size):
    result = ''
    for i in range(0, size):
        result += '0'
    return result

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
HTTPS_PREFIX = 'https://'

def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    if url.endswith('_'):
        url = url[:len(url) - 1]
    return url.replace('/', '_')
