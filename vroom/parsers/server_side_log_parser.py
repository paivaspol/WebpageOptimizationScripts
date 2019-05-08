from argparse import ArgumentParser
from collections import defaultdict

def main(server_side_logs_dir, output_dir):
    pages = os.listdir(server_side_logs_dir)
    for page in pages:
        server_side_log_filename = os.path.join(server_side_logs_dir, page)
        timings = parse_server_side_log(server_side_log_filename)
        output_to_file(output_dir, page, timings)

def parse_server_side_log(server_side_log_filename):
    with open(server_side_log_filename, 'rb') as input_file:
        url_to_recv_req = defaultdict(list)
        url_to_processing_time = defaultdict(list)
        for raw_line in input_file:
            line = raw_line.strip().split()
            port = line[7].split(':')[1]
            scheme = 'https://' if port == '443' else 'http://'
            host = line[6]
            path = line[2]
            url = scheme + host + path
            escaped_url = common_module.escape_page(url)
            url_to_recv_req[url].append(line[0])
            url_to_processing_time[url].append(line[4])
        return url_to_recv_req, url_to_processing_time

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('server_side_logs_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.server_side_logs_dir)
