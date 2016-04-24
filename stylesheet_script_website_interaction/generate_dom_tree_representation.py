from argparse import ArgumentParser
from bs4 import BeautifulSoup, NavigableString

import common_module
import os
import numpy
import json
import gzip

def process_directories(root_dir, ignore_pages):
    pages = os.listdir(root_dir)
    if ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, ignore_pages)
    for directory in pages:
        # if directory != 'apple.com':
        #     continue

        original_html_file = os.path.join(root_dir, directory, 'before_page_load.html')
        if os.path.exists(original_html_file):
            dom_tree = get_page_tree_object(original_html_file)
            ir, mean_tree_depth = generate_ir(dom_tree)
            line = directory + ' ' + str(len(ir)) + ' ' + str(mean_tree_depth)
            if args.output_files is not None:
                json_size, gzip_size = write_ir_to_disk(ir, directory, args.output_files)
                line += ' ' + str(json_size) + ' ' + str(gzip_size)
            print line

def write_ir_to_disk(ir, page, output_dir):
    output_filename = os.path.join(output_dir, page)
    gzip_output_filename = os.path.join(output_dir, page + '.gz')
    with open(output_filename, 'wb') as output_file:
        json.dump(ir, output_file, separators=(',', ':'))
    with gzip.open(gzip_output_filename, 'wb') as gzip_output_file:
        json_str = json.dumps(ir, separators=(',',':'))
        gzip_output_file.write(json_str)
    return os.path.getsize(output_filename), os.path.getsize(gzip_output_filename)

def generate_ir(dom_tree):
    tag_id_tuple_to_positions = dict() # A mapping from <tag_name, classes, id> to positions in the DOM Tree.
    process_queue = [ (dom_tree.html, []) ]
    while len(process_queue) > 0:
        current_element, position_id_list = process_queue.pop(0)

        # print extracted_info
        extracted_info = extract_tag_information(current_element)
        if extracted_info is not None:
            if extracted_info not in tag_id_tuple_to_positions:
                tag_id_tuple_to_positions[extracted_info] = list()
            tag_id_tuple_to_positions[extracted_info].append(position_id_list)
        if hasattr(current_element, 'children'):
            # print str(current_element.name) + ' ' + str(current_element.name != 'head')
            # print ' pos id: ' + str(position_id_list)
            for i, child in enumerate(current_element.children):
                if type(child) != NavigableString and check_can_apply_style_or_id(child):
                    copy_of_pos_id = list(position_id_list)
                    copy_of_pos_id.append(i)
                    process_queue.append((child, copy_of_pos_id))
    mean_tree_depth = numpy.mean([ len(positions) for key, positions in tag_id_tuple_to_positions.iteritems() ])
    return tag_id_tuple_to_positions, mean_tree_depth

def check_can_apply_style_or_id(element):
    return not (element.name == 'head' or element.name == 'meta' or element.name == 'script')

def extract_tag_information(element):
    element_classes = []
    element_id = '$na'
    if hasattr(element, 'attrs'):
        attributes = element.attrs
        if 'class' in attributes:
            element_classes = attributes['class']
        if 'id' in attributes and attributes['id'] is not None:
            element_id = attributes['id']
    class_string = ''
    for element_class in element_classes:
        class_string += element_class.encode('ascii', 'ignore') + ','
    class_string = class_string[:len(class_string) - 1]
    if element.name is None:
        return None
    else:
        return str(element.name.encode('ascii', 'ignore')) + ';' + class_string + ';' + str(element_id.encode('ascii', 'ignore'))

def get_page_tree_object(html_filename):
    return BeautifulSoup(open(html_filename), 'html.parser')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--output-files', default=None)
    args = parser.parse_args()
    process_directories(args.root_dir, args.ignore_pages)
