from argparse import ArgumentParser
from urlparse import urlparse
from multiprocessing import Pool, freeze_support

import subprocess
import os
import itertools

NUM_PROCESSES = 4

def beautify_files(root_dir):
    dirs = os.listdir(root_dir)
    worker_pool = Pool(NUM_PROCESSES)
    worker_pool.map(beautify_page_wrapper, itertools.izip(itertools.repeat(root_dir), \
                                                  dirs))

def beautify_page_wrapper(args):
    return beautify_page(*args)

def beautify_page(root_dir, directory):
    print 'processing: ' + directory
    base_dir = os.path.join(root_dir, directory)
    request_id_to_url_mapping_filename = os.path.join(base_dir, 'request_id_to_url.txt')
    if not os.path.exists(request_id_to_url_mapping_filename):
        return;
    request_id_to_url_map = get_request_id_to_url_map(request_id_to_url_mapping_filename)
    for filename in request_id_to_url_map:
        beautify_file(base_dir, filename, request_id_to_url_map)

def beautify_file(base_dir, request_id, request_id_to_url):
    output_filename = os.path.join(base_dir, request_id + '.beautified')
    if os.path.exists(output_filename):
        return;
    input_filename = os.path.join(base_dir, request_id)
    url = request_id_to_url[request_id]
    parsed_url = urlparse(url)
    # if parsed_url.path.endswith('html'):
    #     cmd = 'html'
    # elif parsed_url.path.endswith('css'):
    #     cmd = 'css'
    if '.js' in parsed_url.path:
          cmd = 'js'
    else:
        return

    cmd += '-beautify -f {0} -o {1}'.format(input_filename, output_filename)
    subprocess.call(cmd.split())

def get_request_id_to_url_map(request_id_to_url_filename):
    result = dict()
    with open(request_id_to_url_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = line[1]
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    freeze_support()
    beautify_files(args.root_dir)
