from argparse import ArgumentParser

import os

def get_line_differences(root_dir):
    for directory in os.listdir(root_dir):
        before_page_load_filename = \
                os.path.join(root_dir, directory, 'before_page_load.html')
        after_page_load_filename = \
                os.path.join(root_dir, directory, 'after_page_load.html')
        if not (os.path.exists(before_page_load_filename) \
                and os.path.exists(after_page_load_filename)):
            continue
        before_page_load_line_count = get_line_count(before_page_load_filename)
        after_page_load_line_count = get_line_count(after_page_load_filename)
        difference = after_page_load_line_count - before_page_load_line_count
        print '{0} {1} {2} {3}'.format(directory, before_page_load_line_count, \
                after_page_load_line_count, difference)
        
def get_line_count(html_file):
    with open(html_file, 'rb') as input_file:
        return sum([ 1 for x in input_file ])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    get_line_differences(args.root_dir)
