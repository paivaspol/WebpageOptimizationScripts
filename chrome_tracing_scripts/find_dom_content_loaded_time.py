from argparse import ArgumentParser

import json
import os

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        network_filename = os.path.join(root_dir, 'network_' + page)
        unknown_filename = os.path.join(root_dir, 'unknown_' + page)

        dom_content_loaded_time = get_dom_content_loaded_time(unknown_filename)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
