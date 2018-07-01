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


def GetURLs(network_filename):
    '''
    Returns a set containing the URLs of the requests.
    '''
    import json
    urls = set()
    found_first_request = False
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                if not found_first_request:
                    found_first_request = True
                    continue

                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue 
                urls.add(url)
    return urls
 
