from argparse import ArgumentParser

import common_module
import urllib
import os
import subprocess

def main():
    pages = common_module.get_pages(args.page_list)
    prefixed_pages = {}
    for page in pages:
        hostname = args.prefix if args.prefix.endswith('/') else args.prefix + '/'
        query = { 'dstPage': page }
        prefixed_page = '{0}prefetch?{1}'.format(hostname, urllib.urlencode(query))
        prefixed_pages[common_module.escape_url(prefixed_page)] = common_module.escape_url(page)

    for i in range(0, args.iterations):
        iter_dir = os.path.join(args.root_dir, str(i))
        for p in os.listdir(iter_dir):
            if p not in prefixed_pages:
                continue
            non_prefixed_page = prefixed_pages[p]
            src = os.path.join(iter_dir, p)
            dst = os.path.join(iter_dir, non_prefixed_page)
            mv_cmd = 'mv {0} {1}'.format(src, dst)
            subprocess.call(mv_cmd.split(' '))
                

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('iterations', type=int)
    parser.add_argument('page_list')
    parser.add_argument('prefix')
    args = parser.parse_args()
    main()
