'''
Finds the count of DOM nodes difference.
'''
from argparse import ArgumentParser

import common_module
import subprocess
import os

PATH = '/Users/vaspol/Documents/research/MobileWebPageOptimization/hdp/page_comparator/dom-compare'

def Main():
    pages = common_module.GetPages(args.page_list)
    total_pages = 0
    did_match_pages = 0
    for p in pages:
        escaped_page = common_module.EscapePage(p)
        dom_a_file = os.path.join(args.dir_dom_a, escaped_page, 'dom')
        dom_b_file = os.path.join(args.dir_dom_b, escaped_page, 'dom')
        if not (os.path.exists(dom_a_file) and os.path.exists(dom_b_file)):
            continue
        compare_cmd = 'python {0}/find_tree_diff.py {1} {2} --hdp'.format(PATH, dom_a_file, dom_b_file)
        if args.only_structure:
            compare_cmd += ' --only-structure'
        try:
            output = subprocess.check_output(compare_cmd.split())
            print '{0} {1}'.format(p, output.strip())
        except Exception as e:
            pass


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dir_dom_a')
    parser.add_argument('dir_dom_b')
    parser.add_argument('page_list')
    parser.add_argument('--only-structure', default=False, action='store_true')
    args = parser.parse_args()
    Main()
