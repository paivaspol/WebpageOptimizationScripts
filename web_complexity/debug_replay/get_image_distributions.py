from argparse import ArgumentParser

import json

# Constants for image MIME types. image/svg is considered text, so we ignore it.
IMG_MIME = {
    'image/png',
    'image/x-png',
    'image/gif',
    'image/jpg',
    'image/jpeg',
    'image/x-icon',
    'image/webp',
    'image/bmp',
    'image/vnd.microsoft.icon',
    'image/ttf',
}

def Main():
    with open(args.requests_filename, 'r') as input_file:
        for l in input_file:
            entry = json.loads(l.strip())
            payload = json.loads(entry['payload'])
            mime_type = GetMimeType(payload)
            if mime_type in IMG_MIME:
                content_length = GetContentLength(payload)
                if content_length > 0:
                    print('{0} {1}'.format(mime_type, content_length))

def GetContentLength(payload):
    resp_headers = payload['response']['headers']
    for header in resp_headers:
        name = header['name']
        value = header['value']
        if name.lower() == 'content-length':
            return int(value)
    return -1

def GetMimeType(payload):
    resp_headers = payload['response']['headers']
    for header in resp_headers:
        name = header['name']
        value = header['value']
        if name.lower() == 'content-type':
            return value
    return ''


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('requests_filename')
    args = parser.parse_args()
    Main()
