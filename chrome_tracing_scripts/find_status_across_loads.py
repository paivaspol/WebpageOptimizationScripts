from argparse import ArgumentParser
from collections import defaultdict

import common_module
import constants
import os
import simplejson as json

def main(root_dir, iterations, pages, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for page in pages:
        page_result = defaultdict(list)
        for i in range(0, iterations):
            network_filename = os.path.join(root_dir, str(i), page, 'network_' + page)
            if not os.path.exists(network_filename):
                continue
            url_to_response = get_response_status(network_filename, page)
            populate_response_status(url_to_response, page_result, i)
        sorted_page_result = sort_on_response_count(page_result)
        output_to_file(output_dir, page, sorted_page_result)

def sort_on_response_count(page_result):
    page_count = dict()
    for url in page_result:
        page_count[url] = sum([ 1 for x in page_result[url] if x >= 0 ])
    sorted_page_count = sorted(page_count.iteritems(), key=lambda x: x[1], reverse=True)
    result = []
    for url, count in sorted_page_count:
        result.append( (url, page_result[url]) )
    return result

def output_to_file(output_dir, page, page_result):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for url, status_code in page_result:
            output_line = url
            for code in status_code:
                output_line += ' ' + str(code)
            output_file.write(output_line + '\n')

def populate_response_status(url_to_response, page_result, iteration):
    if iteration == 0:
        for url in url_to_response:
            page_result[url].append(url_to_response[url])
    else:
        new_urls = set(url_to_response.keys())
        for url in page_result:
            if url not in new_urls:
                page_result[url].append(-1)

        for url in url_to_response:
            if url not in page_result:
                for i in range(0, iteration):
                    page_result[url].append(-1)
            page_result[url].append(url_to_response[url])

def get_response_status(network_filename, page):
    request_id_to_url = dict()
    request_id_to_response_code = dict()
    finished_requests = set()
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == constants.NET_REQUEST_WILL_BE_SENT:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if not found_first_request:
                    if page == common_module.escape_page(url):
                        found_first_request = True
                    else:
                        continue
                request_id_to_url[request_id] = url
            elif network_event[constants.METHOD] == constants.NET_RESPONSE_RECEIVED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                status = network_event[constants.PARAMS][constants.RESPONSE][constants.STATUS]
                if request_id in request_id_to_url:
                    request_id_to_response_code[request_id] = status
            elif network_event[constants.METHOD] == constants.NET_LOADING_FINISHED:
                request_id = network_event[constants.PARAMS][constants.REQUEST_ID]
                finished_requests.add(request_id)

    # Find unfinished requests.
    unfinished_requests = set(request_id_to_url.keys()) - finished_requests
    for unfinished_request in unfinished_requests:
        del request_id_to_url[unfinished_request]
        if unfinished_request in request_id_to_response_code:
            del request_id_to_response_code[unfinished_request]

    # Return URL to status code mapping
    result = dict()
    for request_id in request_id_to_url:
        url = request_id_to_url[request_id]
        status = request_id_to_response_code[request_id]
        result[url] = status
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('iterations', type=int)
    parser.add_argument('page_list')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    page_list = common_module.get_pages(args.page_list)
    main(args.root_dir, args.iterations, page_list, args.output_dir)
