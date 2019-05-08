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


def RemoveQuery(url):
    from urlparse import urlparse
    parsed_url = urlparse(url)
    return parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path


def GetResponseBodiesUrls(response_bodies_filename):
    '''Returns a set of URLs with response bodies.'''
    import json

    urls_with_bodies = set()
    with open(response_bodies_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            urls_with_bodies.add(entry['url'])
    return urls_with_bodies


def GetUrlsFromHttpArchive(requests_filename, response_bodies_filename):
    '''
    Returns a tuple of two sets:
        <urls_with_response_bodies, urls_that_needs_fetching>.
    '''
    import json

    urls_with_bodies = GetResponseBodiesUrls(response_bodies_filename)
    fetched_urls = set()

    # Find the remaining URLs.
    with open(requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            url = entry['url']
            if url not in urls_with_bodies:
                fetched_urls.add(url)
    return (urls_with_bodies, fetched_urls)


def StatusCodeMappingFromRun(experiment_network_filename):
    import json

    with open(experiment_network_filename, 'r') as input_file:
        retval = {}
        requested_urls = {}
        for l in input_file:
            event = json.loads(l.strip())
            if event['method'] == 'Network.requestWillBeSent':
                url = event['params']['request']['url']
                request_id = event['params']['requestId']
                requested_urls[request_id] = url
            elif event['method'] == 'Network.responseReceived':
                url = event['params']['response']['url']
                status_code = event['params']['response']['status']
                retval[url] = status_code
            elif event['method'] == 'Network.loadingFailed':
                request_id = event['params']['requestId']
                retval[requested_urls[request_id]] = 404
        return retval


def HandleError(e):
    '''Utility function for error callbacks.'''
    import traceback

    print(''.join(traceback.format_tb(e.__traceback__)))
    tb = traceback.format_exc()
    print(repr(tb))


def ExtractRefererFromHAEntry(entry):
    '''Returns the request referer.'''
    headers = entry['request']['headers']
    for h in headers:
        if h['name'].lower() == 'referer':
            return h['value']
    return None


def GetCrawledFiles(response_bodies_filename):
    '''Returns a dictionary mapping from page URL to a set of crawled URLs.'''
    from collections import defaultdict
    import json

    result = defaultdict(set)
    with open(response_bodies_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            result[escape_page(entry['page'])].add(entry['url'])
    return result


def GetTimestampSinceEpochMs(datetime_str):
    '''Returns an int representing the timestamp since epoch.'''
    from dateutil.parser import parse

    import datetime

    parsed_ts = parse(datetime_str).replace(tzinfo=None)
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (parsed_ts - epoch).total_seconds() * 1000.0


def GetFrameBreakdown(sorted_requests, main_frame_id):
    '''Returns a tuple of ( list(first_party resources), dict[iframe] -->
    list(resources) ).

    This assumes that sorted_requests: (url, request ts (ms), frame_id) on
    the request ts.'''
    from collections import defaultdict

    seen_frames = set()
    first_party = []
    third_party = defaultdict(list)
    frame_id_to_iframe_url = {}
    for url, _, frame_id, referer in sorted_requests:
        iframe_id = (frame_id, referer)
        if frame_id not in seen_frames:
            seen_frames.add(frame_id)
            frame_id_to_iframe_url[frame_id] = url if frame_id != '-1' else '[NOT_FOUND]'
        if frame_id == main_frame_id:
            first_party.append(url)
        else:
            third_party[frame_id_to_iframe_url[frame_id]].append(url)
    return (first_party, third_party)


def GetLoadTimesTsMs(pages_filename):
    '''Returns a dictionary mapping from pageurl --> timestamp of the onload
    event in ms'''
    import json

    with open(pages_filename, 'r') as input_file:
        page_load_times = {}
        for l in input_file:
            entry = json.loads(l.strip())
            pageurl = entry['url']
            payload = json.loads(entry['payload'])
            load_time = payload['_loadTime']
            # Timestamp example: 2019-01-14T15:56:49.574+00:00
            start_ts_epoch_ms = GetTimestampSinceEpochMs(payload['startedDateTime'])
            page_load_times[escape_page(pageurl)] = start_ts_epoch_ms + load_time
    return page_load_times


def GetReplayPltMs(plt_filename):
    '''Returns the PLT value in ms.'''
    with open(plt_filename, 'r') as input_file:
        line = input_file.read().strip().split()
        end_nav = int(line[2])
        start_nav = int(line[1])
        return end_nav - start_nav


def GetMimeTypeFromHAR(payload):
    '''Returns the MIME type from the HAR object.'''
    resp_headers = payload['response']['headers']
    for header in resp_headers:
        name = header['name']
        value = header['value']
        if name.lower() == 'content-type':
            return value
    return ''
