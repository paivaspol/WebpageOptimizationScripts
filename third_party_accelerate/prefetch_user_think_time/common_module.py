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
            if l.startswith('#') or len(l.strip()) == 0:
                continue
            urls.append(l.strip())
    return urls
 

def RemoveFragments(url):
    from urlparse import urlparse
    parsed_url = urlparse(url, allow_fragments=False)
    return parsed_url.geturl()


def GetURLs(network_filename):
    '''
    Returns a set containing the URLs of the requests.
    '''
    import json
    urls = set()
    first_request = None
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                if first_request is None:
                    first_request = e['params']['request']['url']
                    continue

                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue 
                urls.add(url)

    if first_request is None:
        return None, None
    return urls, RemoveFragments(first_request)


def GetURLsAndResourceSizes(network_filename):
    '''
    Returns a set containing the URLs of the requests.
    '''
    import json
    urls = set()
    resource_sizes = {}
    req_id_to_url = {}
    first_request = None
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                if first_request is None:
                    first_request = e['params']['request']['url']
                    continue

                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue 
                urls.add(url)
                req_id_to_url[e['params']['requestId']] = url
            elif e['method'] == 'Network.loadingFinished':
                request_id = e['params']['requestId']
                if request_id not in req_id_to_url:
                    continue
                url = req_id_to_url[request_id]
                resource_sizes[url] = e['params']['encodedDataLength']

    if first_request is None:
        return None, None, None
    return urls, RemoveFragments(first_request), resource_sizes



def GetBasePage(path):
    splitted_path = path.split('/')
    retval = splitted_path[len(splitted_path) - 1] 
    if retval == '0':
        retval = splitted_path[len(splitted_path) - 2]
    return retval


def GetFirstTwoTokens(url):
    '''
    Takes the url and returns the first two token of the URL
    separated by an underscore.
    '''
    escaped = EscapeURL(url)
    splitted = escaped.split('_')
    return '_'.join(splitted[:2])


def GetUrlsWithMostCommonPrefix(urls):
    '''
    Returns a list of URLs with the most common prefix
    '''
    from collections import defaultdict
    histogram = defaultdict(int)
    for url in urls:
        prefix = GetFirstTwoTokens(url)
        histogram[prefix] += 1
    sorted_histogram = sorted(histogram.items(), key=lambda x: x[1], reverse=True)
    chosen_prefix = sorted_histogram[0][0]
    filtered = []
    for url in urls:
        if not url.startswith(chosen_prefix):
            continue
        filtered.append(url)
    return filtered


def FilterUrlsFromDifferentDomain(lp_domain, urls):
    '''
    Returns a list of URLs from the lp_domain.
    '''
    retval = []
    for url in urls:
        escaped = EscapeURL(url)
        splitted = escaped.split('_')
        first_token = splitted[0]
        if lp_domain not in first_token:
            continue
        retval.append(url)
    return retval


def GetUrlsAndCacheTimes(network_filename, expiry_time_threshold=-1):
    import json
    urls = set()
    cache_times = {}
    with open(network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                if not url.startswith('http'):
                    continue
                urls.add(url)
            elif e['method'] == 'Network.responseReceived':
                url = e['params']['response']['url']
                if not url.startswith('http'):
                    continue
                cache_time = ParseCacheTime(e['params']['response']['headers'])
                if cache_time <= expiry_time_threshold and url in urls:
                    urls.remove(url)
                    continue
                cache_times[url] = cache_time
    return urls, cache_times


def ParseCacheTime(headers):
    '''
    Returns the cache time, in seconds.
    '''
    if 'cache-control' not in headers:
        return 0
    cache_value = headers['cache-control'].split('=')
    for i, v in enumerate(cache_value):
        if v == 'max-age':
            cache_policy = cache_value[i + 1]
            retval = ''
            found_non_int = False
            for c in cache_policy:
                if not found_non_int and c.isdigit():
                    retval += c
                else:
                    found_non_int = True
            return int(retval)
    return 0
