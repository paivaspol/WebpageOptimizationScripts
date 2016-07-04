from argparse import ArgumentParser

import os

CHILDREN_SOURCES = [ 'html', 'css', 'inline_script' ]
SUFFIX = '_children.txt'

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        # if page == 'apple.com':
        #     process_page(root_dir, page)
        process_page(root_dir, page)

def process_page(root_dir, page):
    page_dir = os.path.join(root_dir, page)
    actual_dir = os.path.join(page_dir, 'actual')
    result = dict()

    if args.mode == 'overestimated-to-all':
        union_of_children = get_urls(os.path.join(actual_dir, 'all' + SUFFIX))

    print page
    for children_source in CHILDREN_SOURCES:
        extracted_urls = get_urls(os.path.join(page_dir, children_source + SUFFIX))
        actual_urls = get_urls(os.path.join(actual_dir, children_source + SUFFIX))
        if extracted_urls is None or actual_urls is None:
            continue
        if args.mode == 'miss':
            num_missing_children, missing_children = find_missing_children(actual_urls, extracted_urls, children_source)
            print '\t{0} {1} {2}'.format(children_source, num_missing_children, len(actual_urls))

        elif args.mode == 'overestimate':
            num_overestimated, overestimated_children = find_overestimated_children(actual_urls, extracted_urls)
            print '\t{0} {1} {2}'.format(children_source, num_overestimated, len(actual_urls))

        elif args.mode == 'intersection':
            num_missing_children, missing_children = find_missing_children(actual_urls, extracted_urls)
            num_overestimated, overestimated_children = find_overestimated_children(actual_urls, extracted_urls)
            intersection = missing_children & overestimated_children
            print '\t{0} {1}'.format(children_source, len(intersection))
            if args.print_unmatched:
                print intersection

        elif args.mode == 'overestimated-to-all':
            num_overestimated, overestimated_children = find_overestimated_children(union_of_children, extracted_urls)
            print '\t{0} {1} {2}'.format(children_source, num_overestimated, len(actual_urls))

def get_urls(filename):
    result = list()
    try:
        with open(filename, 'rb') as input_file:
            for raw_line in input_file:
                result.append(raw_line.strip())
    except Exception as e:
        pass
    return result

def find_missing_children(actual_children, extracted_children, children_source):
    missing_children = set() 
    for actual_child in actual_children:
        # print 'extracted: ' + extracted_child
        matched = False
        for extracted_child in extracted_children:
            if remove_relative_path(extracted_child) in actual_child or \
                remove_relative_path(actual_child) in extracted_child:
                matched = True
                break
        if not matched:
            missing_children.add(actual_child)
            if args.print_unmatched:
                print '[MISSING]: ' + actual_child
    return len(missing_children), missing_children

def find_overestimated_children(actual_children, extracted_children):
    # print actual_children
    overestimated_children = set()
    for extracted_child in extracted_children:
        # print 'extracted: ' + extracted_child
        matched = False
        for actual_child in actual_children:
            if remove_relative_path(extracted_child) in actual_child or \
                remove_relative_path(actual_child) in extracted_child:
                matched = True
                break
        if not matched:
            overestimated_children.add(extracted_child)
            if args.print_unmatched:
                print '[OVERESTIMATED]: ' + extracted_child
    return len(overestimated_children), overestimated_children

def remove_relative_path(path):
    result = path
    result = result.replace('..', '')
    # result = result.replace('.', '')
    while result.startswith('\/'):
        result = result[1:]
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('mode', choices=[ 'miss', 'overestimate', 'intersection', 'overestimated-to-all' ])
    parser.add_argument('--print-unmatched', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir)

