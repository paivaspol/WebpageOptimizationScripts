HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'

def escape_page(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    if url.endswith('_'):
        url = url[:len(url) - 1]
    return url.replace('/', '_')

def parse_pages_to_ignore(pages_to_ignore_filename):
    pages = set()
    if pages_to_ignore_filename is not None:
        with open(pages_to_ignore_filename, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip()
                pages.add(escape_page(line))
    print pages
    return pages
