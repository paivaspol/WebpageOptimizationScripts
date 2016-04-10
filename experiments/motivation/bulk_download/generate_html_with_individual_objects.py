from argparse import ArgumentParser

import common_module
import os

def generate_html_files(resource_sizes, output_dir):
    resource_html_filenames = construct_html_for_resources(resource_sizes, output_dir)
    index_html_str = construct_html_header()
    for resource_html_filename in resource_html_filenames:
        index_html_str += construct_iframe_object(resource_html_filename)
    index_html_str += construct_html_footer()
    output_filename = os.path.join(output_dir, 'index.html')
    write_to_file(output_filename, index_html_str)

def construct_html_for_resources(resources, output_dir):
    resource_filename_list = []
    for resource in resources:
        resource_size = resources[resource]
        body = common_module.generate_content(resource_size)
        html_str = construct_html(body)
        html_filename = resource + '.html'
        resource_filename_list.append(html_filename)
        output_filename = os.path.join(output_dir, html_filename)
        write_to_file(output_filename, html_str)
    return resource_filename_list

def construct_iframe_object(src):
    return '<iframe src="{0}" style="dislay: none"></iframe>'.format(src)

def construct_html(body):
    head = construct_html_header()
    footer = construct_html_footer()
    return head + body + footer

def construct_html_header():
    return '<html><head></head><body>'

def construct_html_footer():
    return '</body></html>'

def write_to_file(output_filename, content):
    with open(output_filename, 'wb') as output_file:
        output_file.write(content)

def parse_resource_size_file(page_size_filename):
    result = dict()
    with open(page_size_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

def create_output_dir(output_dir):
    '''
    Creates the output directory.
    '''
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('resource_size_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    resource_sizes = parse_resource_size_file(args.resource_size_filename)
    generate_html_files(resource_sizes, args.output_dir)

