from argparse import ArgumentParser

import json
import os

def main(network_files_dir, extended_waterfall_dir):
    for p in os.listdir(network_files_dir):
        network_filename = os.path.join(network_files_dir, p, 'network_' + p)
        extended_waterfall_filename = os.path.join(extended_waterfall_dir, p, 'timings.txt')
        if os.path.exists(network_filename) and os.path.exists(extended_waterfall_filename):
            all_iframes = get_all_iframes(network_filename)
            start_processing_time = get_start_processing_time(extended_waterfall_filename, all_iframes)
            if start_processing_time[1] != -1:
                # print '{0} {1} {2}'.format(p, start_processing_time[0], start_processing_time[1])
                print '{0} {1}'.format(p, start_processing_time[1])

def get_start_processing_time(extended_waterfall_filename, urls):
    with open(extended_waterfall_filename, 'rb') as input_file:
        result = []
        for l in input_file:
            obj = json.loads(l.strip())
            if obj['url'] in urls and len(obj['processing_time']) > 0:
                result.append((obj['url'], obj['processing_time'][0]))
        if len(result) > 0:
            return sorted(result, key=lambda x: x[0])[0]
        return ('', -1)

def get_all_iframes(network_filename):
    with open(network_filename, 'rb') as input_file:
        all_iframes = set()
        found_first = False
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event['method'] == 'Network.responseReceived' and \
                network_event['params']['type'] == 'Document':
                if not found_first:
                    found_first = True
                else:
                    all_iframes.add(network_event['params']['response']['url'])
        return all_iframes

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_files_dir')
    parser.add_argument('extended_waterfall_dir')
    args = parser.parse_args()
    main(args.network_files_dir, args.extended_waterfall_dir)
