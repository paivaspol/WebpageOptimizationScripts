import os

def get_pages_without_pages_to_ignore(base_pages, pages_to_ignore_filename):
    pages_to_ignore = set()
    with open(pages_to_ignore_filename, 'rb') as input_file:
        for raw_line in input_file:
            pages_to_ignore.add(raw_line.strip())
    base_pages_set = set(base_pages)
    return base_pages_set - pages_to_ignore

def setup_directory(output_dir, page):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))

def create_directory_if_not_exists(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory

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

def get_pages(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ escape_page(line[len(line) - 1]) for line in temp ]

def get_pages_with_redirection(page_list_filename):
    with open(page_list_filename, 'rb') as input_file:
        temp = [ line.strip().split() for line in input_file ]
        return [ (escape_page(line[0]), escape_page(line[len(line) - 1])) for line in temp if not line[0].startswith('#') ]
