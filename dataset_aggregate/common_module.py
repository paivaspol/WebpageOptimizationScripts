def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ (escape_page(line[0]), escape_page(line[len(line) - 1])) for line in temp ]

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
