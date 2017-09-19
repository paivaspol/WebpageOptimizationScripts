from argparse import ArgumentParser

import json

def main(timing_file, output_filename):
    with open(timing_file, 'rb') as input_file, \
        open(output_filename, 'wb') as output_file:
        for raw_line in input_file:
            timing = json.loads(raw_line.strip())
            url = timing['url']
            network_wait_time = timing['ResourceFinish'] - timing['ResourceSendRequest']
            processing_time = 0 if len(timing['processing_time']) == 0 else timing['processing_time'][1] - timing['processing_time'][0]
            output_line = '{0} {1} {2}'.format(url, network_wait_time, processing_time)
            output_file.write(output_line + '\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('timing_file')
    parser.add_argument('output_filename')
    args = parser.parse_args()
    main(args.timing_file, args.output_filename)
