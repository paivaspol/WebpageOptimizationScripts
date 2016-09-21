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
        temp = [ line.strip().split() for line in input_file ]
        return [ escape_page(line[len(line) - 1]) for line in temp ]

def extract_url_from_link_string(link_string):
    # First, split by space.
    result_urls = set()
    splitted_link_string = link_string.split(' ')
    for link_token in splitted_link_string:
        splitted_link_token = link_token.split(';')
        if len(splitted_link_token) >= 3:
            url = splitted_link_token[0]
            rel = splitted_link_token[1]
            try:
                _, rel_type = rel.split('=')
                if rel_type == 'preload':
                    result_urls.add(url[1:len(url) - 1]) # Remove < and > at the beginning and end of string
            except Exception as e:
                pass
                
    return result_urls
