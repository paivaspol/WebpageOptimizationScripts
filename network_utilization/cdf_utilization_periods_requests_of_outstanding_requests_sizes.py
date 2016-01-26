from argparse import ArgumentParser

def find_request_to_size_dict(requests_to_sizes_filename):
    '''
    Returns a dictionary mapping from the request id to the size of the request.
    '''
    result = dict()
    with open(requests_to_sizes_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            request_id = line[0]
            size = int(line[1])
            result[request_id] = size
    return result

def find_intervals_based_on_threshold(network_events, request_to_size_dict, threshold):
    outstanding_request_size = 0
    for network_event in network_events:
        

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_events_filename')
    parser.add_argument('page_start_end_time_filename')
    parser.add_argument('pcap_filename')
    parser.add_argument('requests_to_sizes_filename')
    parser.add_argument('bytes_threshold', type=int)
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    page_start_end_time = common_module.parse_page_start_end_time(args.page_start_end_time_filename)
    network_events = common_module.parse_network_events(args.network_events_filename)
    request_to_size_dict = find_request_to_size_dict(args.requests_to_sizes_filename)
