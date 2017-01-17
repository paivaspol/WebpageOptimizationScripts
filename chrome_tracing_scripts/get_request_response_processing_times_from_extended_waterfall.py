from argparse import ArgumentParser

import os

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        result = generate_data(root_dir, page)
        output_to_file(output_dir, page, result)

def output_to_file(output_dir, page, result):
    output_filename = os.path.join(output_dir, page)
    with open(output_filename, 'wb') as output_file:
        for url in result:
            for timing in result[url]:
                output_line = url
                if len(timing) >= 3:
                    for t in timing:
                        output_line += ' ' + str(t)
                    output_file.write(output_line + '\n')

def generate_data(root_dir, page):
    # ResourceFinish.txt           ResourceReceiveResponse.txt  ResourceSendRequest.txt      processing_time.txt
    resource_send_request_filename = os.path.join(root_dir, page, 'ResourceSendRequest.txt')
    resource_finish_filename = os.path.join(root_dir, page, 'ResourceFinish.txt')
    resource_receive_response_filename = os.path.join(root_dir, page, 'ResourceReceiveResponse.txt')       
    processing_time_filename = os.path.join(root_dir, page, 'processing_time.txt')
    result = populate_request_times(resource_send_request_filename)
    populate_other_timings(resource_receive_response_filename, result)
    populate_other_timings(resource_finish_filename, result)
    populate_other_timings(processing_time_filename, result)
    return result

def populate_other_timings(timing_filename, result_dict, enable_debug=False):
    with open(timing_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            request_id = line[1]

            if url in result_dict:
                url_timings = result_dict[url]
                for time in line[2:]:
                    # Find the appropriated slot to place this timing.
                    cur_max_request_time = -1
                    target_index = -1
                    for i in range(0, len(url_timings)):
                        timing = url_timings[i]
                        if time > cur_max_request_time and \
                            timing[0] > cur_max_request_time:
                            target_index = i
                            cur_max_request_time = timing[0]
                    url_timings[target_index].append(time)

def populate_request_times(resource_send_request_filename):
    result = dict()
    with open(resource_send_request_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            request_id = line[1]
            time = int(line[2])
            if url not in result:
                result[url] = []
            result[url].append([ time ]) # add new list for each of the entries.
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
