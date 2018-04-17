from argparse import ArgumentParser
from shutil import copyfile, rmtree

import common_module
import subprocess
import os

PATH = '/Users/vaspol/Documents/research/MobileWebPageOptimization/hdp/page_comparator/dom-compare'

def Main():
    latest_n_dirs = GetLatestNDirs(args.crawl_dir, args.n_latest)
    pages = common_module.GetPages(args.page_list)
    if os.path.exists(args.output_dir):
        rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    for p in pages:
        escaped_page = common_module.EscapePage(p)
        # Setup the page output dir
        page_output_dir = os.path.join(args.output_dir, escaped_page)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)

        print latest_n_dirs
        first_count = -1
        for i, d in enumerate(latest_n_dirs):
            d = str(d)
            # Setup the intersection after each comparison
            tmp_compare_result = os.path.join(page_output_dir, str(i))
            if not os.path.exists(tmp_compare_result):
                os.mkdir(tmp_compare_result)
            print tmp_compare_result

            if i == 0:
                base_filename = os.path.join(args.crawl_dir, d, '0', escaped_page, 'dom')
                if not os.path.exists(base_filename):
                    break

                # First dir. Set this up as the base DOM tree.
                copyfile(base_filename, os.path.join(tmp_compare_result, 'dom'))
                continue

            dom_a_file = os.path.join(os.path.join(page_output_dir, str(i - 1)), 'dom')
            dom_b_file = os.path.join(args.crawl_dir, d, '0', escaped_page, 'dom')
            if not (os.path.exists(dom_a_file) and os.path.exists(dom_b_file)):
                continue

            compare_cmd = 'python {0}/find_tree_diff.py {1} {2} --hdp --dump-common-tree {3}'.format(PATH, dom_a_file, dom_b_file, os.path.join(tmp_compare_result, 'dom'))

            if args.only_structure:
                compare_cmd += ' --only-structure'

            try:
                print compare_cmd
                output = subprocess.check_output(compare_cmd.split())
                output_filename = os.path.join(args.output_dir, str(i))
                with open(output_filename, 'a') as output_file:
                    splitted = output.strip().split()
                    intersect_count = splitted[0]
                    if first_count == -1:
                        first_count = splitted[1]
                    output_file.write('{0} {1} {2}\n'.format(p, intersect_count, first_count))
            except Exception as e:
                print e
                pass


def GetLatestNDirs(crawl_dir, n_latest):
    all_dirs = os.listdir(crawl_dir)
    print all_dirs
    return sorted([ int(x) for x in all_dirs ])[len(all_dirs) - n_latest:]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('crawl_dir')
    parser.add_argument('n_latest', type=int)
    parser.add_argument('page_list')
    parser.add_argument('output_dir')
    parser.add_argument('--only-structure', default=False, action='store_true')
    args = parser.parse_args()
    Main()
