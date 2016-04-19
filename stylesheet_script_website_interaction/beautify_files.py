from argparse import ArgumentParser

import subprocess
import os

def beautify_files(root_dir):
    dirs = os.listdir(root_dir)
    for directory in dirs:
        print 'processing: ' + directory
        base_dir = os.path.join(root_dir, directory, 'response_body')
        request_id_to_url_mapping_filename = os.path.join(base_dir, 'request_id_to_url.txt')
        if not os.path.exists(request_id_to_url_mapping_filename):
            continue
        request_id_to_url_map = get_request_id_to_url_map(request_id_to_url_mapping_filename)
        for filename in request_id_to_url_map:
            output_filename = os.path.join(base_dir, filename + '.beautified')
            if os.path.exists(output_filename):
                break
            beautify_file(base_dir, filename, output_filename, request_id_to_url_map)

def beautify_file(base_dir, request_id, output_filename, request_id_to_url):
    input_filename = os.path.join(base_dir, request_id)
    if request_id_to_url[request_id].endswith('html'):
        cmd = 'html'
    elif request_id_to_url[request_id].endswith('css'):
        cmd = 'css'
    elif request_id_to_url[request_id].endswith('js'):
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
    beautify_files(args.root_dir)
