from argparse import ArgumentParser

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


def Main():
    with open(args.db_file, 'r') as input_file:
        for i, page_info in enumerate(input_file):
            if i == 0:
                # Column headers.
                continue
            page_info = page_info.strip().split()
            url = escape_page(page_info[0])
            total_bytes = page_info[1]
            total_reqs = page_info[2]
            print('{0} {1} {2}'.format(url, total_reqs, total_bytes))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('db_file')
    args = parser.parse_args()
    Main()
