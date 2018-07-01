from argparse import ArgumentParser

import common_module
import os
import shutil
import subprocess

def Main():
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    pages = common_module.GetURLsFromPageList(args.page_list)
    for p in pages:
        escaped_page = common_module.EscapeURL(p)
        # python get_urls_to_analyze.py ../../../results/prefetch-user-think-time/crawl/main_page/0/etsy.com/onload_root_html http://www.etsy.com
        root_html_filename = os.path.join(args.root_dir, escaped_page, 'onload_root_html')
        if not os.path.exists(root_html_filename):
            continue
        command = 'python get_urls_to_analyze.py {0} {1}'.format(root_html_filename, p)
        print command
        output = subprocess.check_output(command.split())
        output_filename = os.path.join(args.output_dir, escaped_page)
        with open(output_filename, 'w') as output_file:
            output_file.write(output)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('page_list')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
