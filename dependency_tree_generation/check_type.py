inconsistent_map = { 
    'image/svg+xml': 'Image',
    'image/png': 'Image',
    'application/json': 'XHR',
    'text/plain': 'XHR',
    'text/html': 'Document',
    'text/javascript': 'Script',
    'text/json': 'XHR',
    'application/javascript': 'Script'
    # 'text/css': 'Style'
}

def check_type(response_type, mime_type):
    if mime_type in inconsistent_map:
        return inconsistent_map[mime_type]
    else:
        return response_type
