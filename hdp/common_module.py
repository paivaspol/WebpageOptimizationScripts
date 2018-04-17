HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
HTTPS_PREFIX = 'https://'


def GetPages(page_list_filename):
    '''
    Returns a list of pages from the page_list_filename
    '''
    with open(page_list_filename, 'r') as input_file:
        return [ l.strip() for l in input_file ]


def EscapePage(url):
    '''
    Escapes the URL.
    '''
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


