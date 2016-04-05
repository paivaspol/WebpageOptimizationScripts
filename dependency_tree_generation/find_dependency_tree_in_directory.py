from argparse import ArgumentParser

import os
import subprocess

import common_module

def traverse_root_directory(root_dir, pages, aggregate_dir):
    for page in pages:
        url = common_module.escape_url(page)
        path = os.path.join(root_dir, url)
        print 'processing: ' + url
        page_start_end_time_filename = os.path.join(path, 'start_end_time_' + url)
        network_events_filename = os.path.join(path, 'network_' + url)
        command = 'python find_dependencies.py {0} {1} {2} --output-dir {3}'.format(page, network_events_filename, page_start_end_time_filename, path)
        subprocess.call(command, shell=True)
        if aggregate_dir is not None:
            dependency_tree_filename = os.path.join(path, 'dependency_graph.json')
            output_filename = os.path.join(aggregate_dir, url + '.json')
            if not os.path.exists(aggregate_dir):
                os.mkdir(aggregate_dir)
            cp_cmd = 'cp {0} {1}'.format(dependency_tree_filename, output_filename)
            subprocess.call(cp_cmd, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_file')
    parser.add_argument('--aggregate-dir', default=None)
    args = parser.parse_args()
    pages = common_module.get_pages(args.pages_file)
    traverse_root_directory(args.root_dir, pages, args.aggregate_dir)
