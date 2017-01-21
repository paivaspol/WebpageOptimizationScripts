from argparse import ArgumentParser

import os

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        send_request_filename = os.path.join(root_dir, page, 'ResourceSendRequest.txt')
        response_filename = os.path.join(root_dir, page, 'ResourceReceiveResponse.txt')
        fetch_filename = os.path.join(root_dir, page, 'ResourceFinish.txt')
        if not (os.path.exists(send_request_filename) and \
            os.path.exists(response_filename) and \
            os.path.exists(fetch_filename)):
            continue
        timings = get_timings(response_filename, fetch_filename)
        if check_overlap(timings):
            print 'PASS'
        else:
            print 'FAILED'
            for url, timing in timings:
                print '{0} {1} {2}'.format(url, timing[0], timing[1])

def check_overlap(timings):
    for i in range(0, len(timings)):
        for j in range(i + 1, len(timings)):
            if is_overlap(timings[i][1], timings[j][1]):
                return False
    return True


def is_overlap(first_int, second_int):
    return not (first_int[1] < second_int[0] or \
                second_int[1] < first_int[0])

def get_request_ordering(request_filename):
    order = []
    with open(request_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            order.append(line[0])
    return order

def get_timings(response_filename, fetch_filename):
    result = []
    response_timing = dict()
    with open(response_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            response_timing[line[0]] = line[2]
    with open(fetch_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            if url in response_timing and \
                ('s0.wp' in url or \
                 's1.wp' in url or \
                 's2.wp' in url):
                result.append((url, (int(response_timing[url]), int(line[2]))))
    return sorted(result, key=lambda x: x[1][0])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
