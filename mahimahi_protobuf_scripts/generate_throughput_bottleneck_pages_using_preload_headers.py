from argparse import ArgumentParser

import http_record_pb2

import common_module
import os
import subprocess

def main(root_dir, pages_to_timestamp, dependencies_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    for page, timestamp in pages_to_timestamp.iteritems():
        page_directory = os.path.join(root_dir, timestamp, page)
        
        # Find the page to resource sizes mapping.
        resource_size_mapping_filename = os.path.join(page_resource_sizes_dir, page)
        dependency_filename = os.path.join(dependencies_dir, page, 'dependency_tree.txt')
        if not os.path.exists(resource_size_mapping_filename) \
            or not os.path.exists(dependency_filename):
            continue
        
        timestamp_output_directory = os.path.join(output_dir, timestamp)
        if not os.path.exists(timestamp_output_directory):
            os.mkdir(timestamp_output_directory)

        # Copy the original recordings to a the new folder.
        page_output_directory = os.path.join(timestamp_output_directory, page)
        command = 'cp -r {0} {1}'.format(page_directory, page_output_directory)
        subprocess.call(command, shell=True)

        resource_urls = common_module.get_dependencies(dependency_filename, False)
        files = os.listdir(page_output_directory)
        top_level_htmls = find_top_level_htmls(files, page_output_directory)
        print top_level_htmls
        for i, top_level_html in enumerate(top_level_htmls):
            top_level_html_full_path = os.path.join(page_output_directory, top_level_html)
            if generate_top_level_html(top_level_html_full_path, resource_urls, page_output_directory, i):
                # Remove the original top-level HTML from the output directory.
                os.remove(top_level_html_full_path)

def generate_top_level_html(top_level_html, resource_urls, output_dir, index):
    # We have to do some modifications to the request response object.
    #   1. Modify the first line in the request
    #   2. Modify the body of the response.
    #   3. Modify the content-length in the response HTTP header.
    with open(top_level_html, 'rb') as input_file:
        file_content = input_file.read()
        main_html_request_response = http_record_pb2.RequestResponse()
        main_html_request_response.ParseFromString(file_content)

        original_content_size = get_header_value(main_html_request_response.response.header, 'content-length')

        # Modify the HTML body
        html_body = generate_html_body(resource_urls, original_content_size)
        main_html_request_response.response.body = html_body
        
        # Modify the content length
        modify_http_header(main_html_request_response.response.header, 'content-length', str(len(html_body)))

        # Strip any kind of encoding: gzip and chunked
        remove_header(main_html_request_response.response.header, 'content-encoding')
        remove_header(main_html_request_response.response.header, 'transfer-encoding')

        output_to_file(main_html_request_response, output_dir, 'index_' + str(index))
        return True

def get_header_value(headers, header_key):
    for header in headers:
        if header.key.lower() == header_key.lower():
            return header.value
    return None

def remove_header(headers, header_key):
    for i in range(0, len(headers)):
        header = headers[i]
        if header.key.lower() == header_key.lower():
            del headers[i]
            break

def find_top_level_htmls(files, base_directory):
    results = []
    for recorded_file in files:
        path_to_file = os.path.join(base_directory, recorded_file)
        temp_filename = 'tmp'
        top_cmd = './protototext {0} {1}'.format(path_to_file, temp_filename)
        proc_top = subprocess.Popen([top_cmd], stdout=subprocess.PIPE, shell=True)
        (out_top, err_top) = proc_top.communicate()
        out_top = out_top.strip("\n")
        if ( "type=htmlindex" in out_top ): # this is the top-level HTML
            top_level_html = out_top.split("na--me=")[1]
            results.append(recorded_file)
        os.remove(temp_filename)
    return results

def get_urls(resource_size_mapping_filename, page):
    results = []
    with open(resource_size_mapping_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if not line[2].startswith('data') and \
                common_module.escape_page(line[2]) != page:
                results.append(line[2])
    return results

def generate_html_body(resource_urls, original_body_size):
    body = '<html><head>'
    link_preload_str = ''
    for resource_url in resource_urls:
        link_preload_str += '<link rel="preload" href ="{0}"></link>'.format(resource_url)
    body += link_preload_str
    body += '</head><body>'
    body += '</body></html>'
    return body

def output_to_file(resource_request_response, output_dir, filename):
    file_content = resource_request_response.SerializeToString()
    output_filename = os.path.join(output_dir, filename)
    with open(output_filename, 'wb') as output_file:
        output_file.write(file_content)

def modify_http_header(http_headers, header_key, header_value):
    for http_header in http_headers:
        if header_key.lower() == http_header.key.lower():
            http_header.value = header_value
            break

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_to_timestamp')
    parser.add_argument('dependencies_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    pages_to_timestamp = common_module.get_page_to_time_mapping(args.pages_to_timestamp)
    main(args.root_dir, pages_to_timestamp, args.dependencies_dir, args.output_dir)
