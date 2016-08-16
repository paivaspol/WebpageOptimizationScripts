from argparse import ArgumentParser
from datetime import datetime


def main(chromium_log_file):
    with open(chromium_log_file, 'rb') as input_file:
        lines = input_file.readlines()
    i = 0
    start_time = None
    timestamps = []
    urls = []
    while i < len(lines):
        line = lines[i]
        if start_time is None and 'Starting Asynchronous' in line:
            splitted_line = line.split(' ')
            timestamp_str = '2016-' + splitted_line[0] + ' ' + splitted_line[1]
            datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            epoch = datetime.utcfromtimestamp(0)
            millis_since_epoch = (datetime_obj - epoch).total_seconds() * 1000.0
            # print '{0:.0f}'.format(millis_since_epoch)
            timestamps.append(millis_since_epoch)
            start_time = millis_since_epoch
            urls.append('index.html')
        elif 'INFO:http_network_transaction.cc(1759)' in line:
            i += 1
            line = lines[i]
            splitted_line = line.split(' ')
            timestamp_str = '2016-' + splitted_line[0] + ' ' + splitted_line[1]
            datetime_obj = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
            epoch = datetime.utcfromtimestamp(0)
            millis_since_epoch = (datetime_obj - epoch).total_seconds() * 1000.0
            # print '{0:.0f}'.format(millis_since_epoch)
            timestamps.append(millis_since_epoch)
            urls.append(splitted_line[len(splitted_line) - 1].strip())
        i += 1
    differences = []
    for i in range(0, len(timestamps) - 1):
        difference = timestamps[i + 1] - timestamps[i]
        differences.append(difference)

    print 'Num Dependencies: {0}'.format(len(urls))
    print timestamps
    print differences
    if args.print_resources:
        print '---------------------------------------------'
        for url in urls:
            print url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('chromium_log_file')
    parser.add_argument('--print-resources', default=False, action='store_true')
    args = parser.parse_args()
    main(args.chromium_log_file)
