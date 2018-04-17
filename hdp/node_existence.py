'''
Finds the count of DOM nodes difference.
'''
from argparse import ArgumentParser

import subprocess
import os

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
HTTPS_PREFIX = 'https://'

def Main():
    pages = GetPages(args.page_list)
    for p in pages:
        escaped_page = EscapePage(p)
        dom_a_file = os.path.join(args.dir_dom_a, escaped_page, 'dom')
        dom_b_file = os.path.join(args.dir_dom_b, escaped_page, 'dom')
        compare_cmd = 'python /Users/vaspol/Documents/research/MobileWebPageOptimization/page_comparator/dom-compare/check_dom_node_exists.py {0} {1} --hdp'.format(dom_a_file, dom_b_file)
        try:
            output = subprocess.check_output(compare_cmd.split())
            exists_count, total_count = GetDOMExistCount(output)
            print '{0} {1} {2}'.format(p, exists_count, total_count)
        except Exception as e:
            pass


def GetDOMExistCount(output):
    '''
    Parses the output for the DOM exist count.
    '''
    splitted = output.split('\n')
    did_match = splitted[0] == 'MATCHED'
    exist_count = -1
    total_count = -1
    for l in splitted:
        if l.startswith('Matched') and exist_count == -1:
            splitted_l = l.split(':')
            exist_count = int(splitted_l[len(splitted_l) - 1])
        elif l.startswith('Total') and total_count == -1:
            splitted_l = l.split(':')
            total_count = int(splitted_l[len(splitted_l) - 1])
    return exist_count, total_count


def GetPages(page_list_filename):
    '''
    Returns a list of pages from the page_list_filename
    '''
    with open(page_list_filename, 'r') as input_file:
        return [ l.strip() for l in input_file ]

def EscapePage(url):
    '''
    Escapes the URL.
    '''
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    if url.endswith('_'):
        url = url[:len(url) - 1]
    return url.replace('/', '_')


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dir_dom_a')
    parser.add_argument('dir_dom_b')
    parser.add_argument('page_list')
    args = parser.parse_args()
    Main()
