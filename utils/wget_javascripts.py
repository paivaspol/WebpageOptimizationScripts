from argparse import ArgumentParser
from urlparse import urlparse

import simplejson as json
import os
import subprocess

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pages = os.listdir(root_dir)
    for page in pages:
        full_path = os.path.join(root_dir, page)
        page_output_dir = os.path.join(output_dir, page)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)

        mapping_filename = os.path.join(page_output_dir, 'script_id_to_url_map.txt')
        counter = 0
        with open(full_path, 'rb') as input_file, open(mapping_filename, 'wb') as output_file:
            mapping = json.load(input_file)
            for url in mapping:
                parsed_url = urlparse(url)
                if parsed_url.path.endswith('.js'):
                    filename = str(counter) + '.js'
                    command = 'wget --no-check-certificate -q {0} -O {1}'.format(url, os.path.join(page_output_dir, filename))
                    subprocess.call(command.split())
                    output_file.write('{0} {1}\n'.format(filename, url))
                    counter += 1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
