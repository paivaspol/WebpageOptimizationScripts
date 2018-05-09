HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'

def EscapeURL(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')


def GetURLsFromPageList(page_list_filename):
    '''
    Returns a list of URLs from the given file.
    '''
    urls = []
    with open(page_list_filename, 'r') as input_file:
        for l in input_file:
            urls.append(l.strip())
    return urls
