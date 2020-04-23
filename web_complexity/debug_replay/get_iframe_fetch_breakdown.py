r'''
This script breaks down the number of resources missing.
'''
from argparse import ArgumentParser

import os

'''Set of MIME type that requires processing.'''
NEEDS_PROCESSING = {
        'application/javascript',
        'application/x-javascript',
        'text/javascript',
        'text/css',
        'text/html',
        'application/json',
        'text/plain',
}

def Main():
    for d in os.listdir(args.root_dir):
        page_missing_filename = os.path.join(args.root_dir, d, 'missing')
        breakdown = ProcessMissingFile(page_missing_filename)
        print('{0} {1} {2}'.format(d, breakdown[0], breakdown[1]))

def ProcessMissingFile(missing_filename):
    '''Returns a tuple: (num_resources_needs_processing, num_resources).'''
    total_missing = 0
    needs_processing = 0
    with open(missing_filename, 'r') as input_file:
        for i, l in enumerate(input_file):
            if not l.startswith('http'):
                # Not a URL continue.
                continue

            total_missing += 1
            l = l.strip().split()
            mime_type = l[1]
            if mime_type in NEEDS_PROCESSING:
                needs_processing += 1
    return (needs_processing, total_missing)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
