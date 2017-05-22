from argparse import ArgumentParser
from collections import defaultdict

import common_module
import os

def main(root_dir, page_list, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = common_module.get_pages_with_redirection(page_list)
    for page_tuple in pages:
        page, page_r = page_tuple
        reverse_proxy_log = os.path.join(root_dir, 'reverse_proxy_logs', page + '.log')
        request_filename = os.path.join(root_dir, 'extended_waterfall', page_r, 'ResourceSendRequest.txt')
        if not (os.path.exists(reverse_proxy_log) and \
                os.path.exists(request_filename)):
            continue
        request_urls = get_requests(request_filename)
        timings = parse_log(reverse_proxy_log, page, request_urls)
        output_to_file(output_dir, page, timings)

def output_to_file(output_dir, page, timings):
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))
    for i in range(0, len(timings)):
        output_filename = os.path.join(output_dir, page, str(i))
        result = []
        for url in timings[i]:
            output_line = [ url ]
            for t in timings[i][url]:
                output_line.append(t)
            result.append(output_line)
        result.sort(key=lambda x: x[1])
        with open(output_filename, 'wb') as output_file:
            for r in result:
                output_line = ''
                for ele in r:
                    output_line += str(ele) + ' '
                output_file.write(output_line.strip() + '\n')

def parse_log(filename, page, request_urls):
    # print request_urls
    input_file = open(filename, 'rb')
    cur_line = input_file.readline()
    url_to_stream_id_pid = dict()
    stream_id_pid_to_url = dict()
    timings = []
    url_counter = defaultdict(lambda: 0)
    while cur_line != '':
        line = cur_line.strip()
        if 'shrpx_http2_upstream.cc' in line and ('HTTP request headers.' in line or \
                                                  'HTTP push request headers.' in line):
            # A request is received from the upstream
            # print 'Reverse Proxy Receive Request from client.'
            timestamp, pid, stream_id, url, input_file = process_rev_proxy_received_request(input_file, line)
            if url not in request_urls:
                cur_line = input_file.readline()
                continue

            # print '{0} {1} {2} {3}'.format(timestamp, pid, stream_id, url)
            key = (stream_id, pid)
            url_to_stream_id_pid[url] = key
            stream_id_pid_to_url[key] = url
            index = url_counter[url]
            if len(timings) < index + 1:
                timings.append(dict())
            # print 'appending recv request'
            timings[index][url] = []
            timings[index][url].append(int(timestamp))
            # print timings

        elif 'shrpx_http_downstream_connection.cc' in line and 'HTTP request headers' in line:
            # A request is sent to the backend webserver
            # print 'Reverse Proxy Send Request to backend'
            timestamp, pid, stream_id, url, input_file = process_rev_proxy_send_request(input_file, line, page)
            if url not in request_urls:
                cur_line = input_file.readline()
                continue
            # print '{0} {1} {2} {3}'.format(timestamp, pid, stream_id, url)
            # print 'appending send request'
            index = url_counter[url]
            if index >= len(timings):
                cur_line = input_file.readline()
                continue
            if url in timings[index]:
                timings[index][url].append(int(timestamp))

        elif 'HTTP response headers.' in line:
            # A response has been received at the reverse proxy.
            # print 'Reverse Proxy received response'
            timestamp, pid, stream_id, _, input_file = process_rev_proxy_recv_response(input_file, line)
            if (stream_id, pid) not in stream_id_pid_to_url:
                cur_line = input_file.readline()
                continue
            url = stream_id_pid_to_url[(stream_id, pid)]
            # print '\tFOUND: ' + url
            # print '{0} {1} {2} {3}'.format(timestamp, pid, stream_id, url)
            index = url_counter[url]
            if index >= len(timings):
                cur_line = input_file.readline()
                continue
            if url not in timings[index]:
                cur_line = input_file.readline()
                continue
            # print 'appending response'
            timings[index][url].append(int(timestamp))
            url_counter[url] += 1

        cur_line = input_file.readline()
    input_file.close()
    return timings

def output_result(timings):
    for timing in timings:
        for url in timing:
            output_line = url
            for t in timing[url]:
                output_line += ' ' + str(t)
            print output_line
        print ''

def process_rev_proxy_received_request(input_file, log_first_line):
    lines, input_file = get_lines(input_file)
    # get the url.
    path = None
    scheme = None
    hostname = None
    # print 'lines: ' + str(lines)
    for line in lines:
        if line.startswith(':path:'):
            path = line.strip().split(' ')[1]
        elif line.startswith(':authority:'):
            hostname = line.strip().split(' ')[1]
        elif line.startswith(':scheme'):
            scheme = line.strip().split(' ')[1]
    # print '(0): {0} {1} {2}'.format(scheme, hostname, path)
    url = scheme + '://' + hostname + path
    timestamp, pid, stream_id = parse_log_first_line(log_first_line)
    return timestamp, pid, stream_id, url, input_file

def process_rev_proxy_send_request(input_file, log_first_line, page):
    lines, input_file = get_lines(input_file)
    # get the url.
    request_first_line = lines[0].strip().split()
    
    scheme = None
    hostname = None
    for line in lines:
        if line.startswith('X-Forwarded-Proto:'):
            scheme = line.strip().split(' ')[1]
        elif line.startswith('Host:'):
            hostname = line.strip().split(' ')[1]
    path = request_first_line[1] # Method URL Version
    if page == 'yahoo.com_news':
        path = path.replace('http:/', 'http://')
        path = path.replace('https:/', 'https://')
    print '(1): {0} {1} {2}'.format(scheme, hostname, path)
    try:
        url = scheme + '://' + hostname + path
        timestamp, pid, stream_id = parse_log_first_line(log_first_line)
        return timestamp, pid, stream_id, url, input_file
    except:
        return (0,0, 0, '-1', input_file)


def process_rev_proxy_recv_response(input_file, log_first_line):
    timestamp, pid, stream_id = parse_log_first_line(log_first_line)
    return timestamp, pid, stream_id, None, input_file

def parse_log_first_line(log_first_line):
    splitted_first_line = log_first_line.strip().split()
    stream_id = splitted_first_line[len(splitted_first_line) - 1].split('=')[1]
    timestamp = splitted_first_line[0]
    pid = splitted_first_line[1]
    return timestamp, pid, stream_id

def get_lines(input_file):
    lines = []
    cur_line = input_file.readline()
    while cur_line != '\n':
        lines.append(cur_line)
        cur_line = input_file.readline()
    return lines, input_file

def get_requests(request_filename):
    result = set()
    with open(request_filename, 'rb') as input_file:
        for raw_line in input_file:
            url = raw_line.strip().split()[0]
            result.add(url)
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('pages_filename')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.pages_filename, args.output_dir)
