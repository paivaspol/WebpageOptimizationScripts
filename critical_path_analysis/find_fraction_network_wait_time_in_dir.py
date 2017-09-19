from argparse import ArgumentParser

import common_module
import os
import subprocess

def main(data_dir, pages_filename, dependency_dir, net_wait_dir):
    pages = common_module.get_pages_with_redirection(pages_filename)
    for page_tuple in pages:
        page, page_r = page_tuple
        timing_filename = os.path.join(data_dir, page_r, 'timings.txt')
        dep_tree_filename = os.path.join(dependency_dir, 'raw_dependency_tree', page_r + '.json')
        dependency_filename = os.path.join(dependency_dir, 'dependency_list_sorted_by_execution_time', page, 'dependency_tree.txt')
        net_wait_filename = os.path.join(net_wait_dir, page_r, 'net_wait_times')
        if not (os.path.exists(dep_tree_filename) and \
                os.path.exists(timing_filename) and \
                os.path.exists(dependency_filename)):
            cmd = '[ERROR] python find_fraction_of_dynamic_resources_on_critical_path.py {0} {1} {2}'.format(dep_tree_filename, timing_filename, dependency_filename)
            # print cmd
            # if not os.path.exists(dep_tree_filename):
            #     print 'missing dependency tree: {0}'.format(dep_tree_filename)
            # if not os.path.exists(timing_filename):
            #     print 'mising timing file: {0}'.format(timing_filename)
            # if not os.path.exists(dependency_filename):
            #     print 'mssing dependency list filename: {0}'.format(dependency_filename)
            continue
        cmd = 'python find_fraction_network_wait_time.py {0} {1} {2} {3}'.format(dep_tree_filename, timing_filename, dependency_filename, net_wait_filename)
        # print cmd
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        print '{0} {1}'.format(page, stdout.strip())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('data_dir')
    parser.add_argument('pages_filename')
    parser.add_argument('dependency_dir')
    parser.add_argument('net_wait_dir')
    args = parser.parse_args()
    main(args.data_dir, args.pages_filename, args.dependency_dir, args.net_wait_dir)
