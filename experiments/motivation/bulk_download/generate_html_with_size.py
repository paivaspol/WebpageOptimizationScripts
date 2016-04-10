from argparse import ArgumentParser

import os

def generate_html_files(page_sizes, output_dir):
    for page in page_sizes:
        page_size = page_sizes[page]
        content = generate_content(page_size)
        html = construct_html(content)
        escaped_url = escape_url(page) + '.html'
        output_filename = os.path.join(output_dir, escaped_url)
        write_to_file(output_filename, html)
        print 'http://localhost/page_load_experiments/' + escaped_url
        
def escape_url(url):
    return url.replace('.', '_')

def construct_html(body):
    head = '<html><head></head><body>'
    footer = '</body></html>'
    return head + body + footer

def generate_content(size):
    result = ''
    for i in range(0, size):
        result += '0'
    return result

def write_to_file(output_filename, content):
    with open(output_filename, 'wb') as output_file:
        output_file.write(content)

def parse_page_size_file(page_size_filename):
    result = dict()
    with open(page_size_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result[line[0]] = int(line[1])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_size_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    page_sizes = parse_page_size_file(args.page_size_filename)
    generate_html_files(page_sizes, args.output_dir)

