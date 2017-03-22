from argparse import ArgumentParser

import common_module
import os
import subprocess

def main(pages_filename, dep_tree_dir, timings_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = common_module.get_pages_with_redirection(pages_filename)
    for page_tuple in pages:
        page, page_r = page_tuple
        page_output_dir = os.path.join(output_dir, page_r)
        print 'Processing: ' + page
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)
        cmd = 'cp {0} {1}'.format(os.path.join(dep_tree_dir, page_r, 'dep_tree.json'), page_output_dir)
        subprocess.call(cmd, shell=True)
        cmd = 'cp {0} {1}'.format(os.path.join(timings_dir, page_r, 'timings.txt'), page_output_dir)
        subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_filename')
    parser.add_argument('dep_tree_dir')
    parser.add_argument('timings_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.pages_filename, args.dep_tree_dir, args.timings_dir, args.output_dir)
