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

def get_dependencies(dependency_filename):
    with open(dependency_filename, 'rb') as input_file:
        return { line.strip().split()[2] for line in input_file }

def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        return [ escape_page(line.strip()) for line in input_file ]
