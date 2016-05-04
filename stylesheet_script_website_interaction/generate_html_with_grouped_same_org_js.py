from argparse import ArgumentParser
from urlparse import urlparse

import common_module
import os
import subprocess

def process_directories(root_dir, output_dir, domain_to_org_filename):
    pages = os.listdir(root_dir)
    domain_to_org = extract_org_names(domain_to_org_filename)
    if args.ignore_pages is not None:
        pages = common_module.get_pages_without_pages_to_ignore(pages, args.ignore_pages)
    for page in pages:
        page_output_dir = os.path.join(output_dir, page)
        process_page(root_dir, page, page_output_dir, domain_to_org)

def process_page(root_dir, page, output_dir, domain_to_org):
    common_module.create_directory_if_not_exists(output_dir)
    current_dir = os.path.join(root_dir, page)
    request_id_to_url_filename = os.path.join(root_dir, page, 'request_id_to_url.txt')
    if not os.path.exists(request_id_to_url_filename):
        return;
    request_id_to_url = common_module.parse_request_to_url(request_id_to_url_filename)
    domain_to_js = dict()
    for request_id, url in request_id_to_url.iteritems():
        parsed_url = urlparse(url)
        request_id_full_path = os.path.join(root_dir, page, request_id)
        if '.js' in parsed_url.path and os.path.exists(request_id_full_path):
            domain = common_module.extract_domain(url)
            if domain in domain_to_org:
                org = domain_to_org[domain]
                if org not in domain_to_js:
                    domain_to_js[org] = []
                domain_to_js[org].append(request_id)

    page_id_to_domain_mapping = dict()
    for i, domain_js_files in enumerate(domain_to_js.iteritems()):
        domain, js_files = domain_js_files
        page_html = generate_html_for_page(js_files)
        html_filename = write_html_to_file(page_html, i, output_dir)
        copy_js_file(js_files, current_dir, output_dir)
        page_id_to_domain_mapping[domain] = i
        print os.path.join(args.prefix, page, html_filename)
    write_page_id_to_domain(page_id_to_domain_mapping, output_dir)

def copy_js_file(js_names, current_dir, output_dir):
    for js_name in js_names:
        src = os.path.join(current_dir, js_name)
        destination = os.path.join(output_dir, js_name)
        command = 'cp {0} {1}'.format(src, destination)
        subprocess.call(command, shell=True)

def write_page_id_to_domain(page_id_to_domain_mapping, output_dir):
    output_filename = os.path.join(output_dir, 'page_id_to_domain_mapping.txt')
    with open(output_filename, 'wb') as output_file:
        for page_id, domain in page_id_to_domain_mapping.iteritems():
            output_file.write('{0} {1}\n'.format(page_id, domain))

def write_html_to_file(html_str, js_name, output_dir):
    html_filename = str(js_name) + '.html'
    output_filename = os.path.join(output_dir, html_filename)
    with open(output_filename, 'wb') as output_file:
        output_file.write(html_str)
    return html_filename

def generate_html_for_page(js_files):
    script_tags = ''
    for js_name in js_files:
        script_tags += '<script src="{0}"></script>'.format(js_name)
    return get_html_prefix() + script_tags + get_html_suffix()

def get_html_prefix():
    return '<html><head></head><body>'

def get_html_suffix():
    return '<body></body></html>'

def extract_org_names(domain_to_org_filename):
    domain_to_org = dict()
    with open(domain_to_org_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            domain_to_org[line[0]] = line[1]
    return domain_to_org

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('domain_to_org_filename')
    parser.add_argument('output_dir')
    parser.add_argument('--ignore-pages', default=None)
    parser.add_argument('--prefix', default='')
    args = parser.parse_args()
    process_directories(args.root_dir, args.output_dir, args.domain_to_org_filename)
