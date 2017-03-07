from argparse import ArgumentParser

import common_module
import os
import subprocess

def main(data_dir, pages_filename, dependency_dir):
    pages = common_module.get_pages_with_redirection(pages_filename)
    for page_tuple in pages:
        page, page_r = page_tuple
        dep_tree_filename = os.path.join(data_dir, page_r, 'dep_tree.json')
        timing_filename = os.path.join(data_dir, page_r, 'timings.txt')
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(dep_tree_filename) and \
                os.path.exists(timing_filename) and \
                os.path.exists(dependency_filename)):
            cmd = '[ERROR] python find_fraction_of_dynamic_resources_on_critical_path.py {0} {1} {2}'.format(dep_tree_filename, timing_filename, dependency_filename)
            continue
        cmd = 'python find_fraction_of_wait_time_of_dynamic_resources_on_critical_path.py {0} {1} {2} {3}'.format(dep_tree_filename, timing_filename, dependency_filename, page_r)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if not stdout.startswith('max') and len(stdout.strip().split(' ')) > 0:
            print '{0} {1}'.format(page, stdout.strip())
        break

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('pages_filename')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.data_dir, args.pages_filename, args.dependency_dir)
