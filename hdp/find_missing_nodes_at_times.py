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
        prev_d = None
        for i, d in enumerate(latest_n_dirs):
            d = str(d)

            if i == 0:
                prev_d = d
                continue

            # Create the directory for the iteration
            iter_dir = os.path.join(page_output_dir, str(i))
            os.mkdir(iter_dir)

            dom_a_file = os.path.join(args.crawl_dir, prev_d, '0', escaped_page, 'dom')
            dom_b_file = os.path.join(args.crawl_dir, d, '0', escaped_page, 'dom')
            prev_d = d

            if not (os.path.exists(dom_a_file) and os.path.exists(dom_b_file)):
                continue

            compare_cmd = 'python {0}/find_tree_diff.py {1} {2} --hdp --dump-missing-nodes {3}'.format(PATH, dom_a_file, dom_b_file, os.path.join(iter_dir, 'missing'))

            if args.only_structure:
                compare_cmd += ' --only-structure'

            try:
                print compare_cmd
                output = subprocess.check_output(compare_cmd.split())
                output_filename = os.path.join(args.output_dir, str(i))
                with open(output_filename, 'a') as output_file:
                    output_file.write('{0} {1}\n'.format(p, output.strip()))
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
