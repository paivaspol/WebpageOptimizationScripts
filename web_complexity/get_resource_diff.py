from argparse import ArgumentParser

def Main():
    first_file_stats = GetStats(args.file_1)
    second_file_stats = GetStats(args.file_2)
    for url in first_file_stats:
        first_num_request = first_file_stats[url][0]
        second_num_request = second_file_stats[url][0]
        first_num_bytes = first_file_stats[url][1]
        second_num_bytes = second_file_stats[url][1]
        print('{0} {1} {2}'.format(url, (second_num_request - first_num_request), (second_num_bytes - first_num_bytes)))


def GetStats(f_name):
    all_stats = {}
    with open(f_name, 'r') as input_file:
        for l in input_file:
            l = l.strip().split()
            url = l[0]
            num_requests = int(l[1])
            num_bytes = int(l[2])
            all_stats[url] = (num_requests, num_bytes)
    return all_stats

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('file_1')
    parser.add_argument('file_2')
    args = parser.parse_args()
    Main()
