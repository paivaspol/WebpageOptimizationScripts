from argparse import ArgumentParser

import json

def Main():
    with open(args.network_filename, 'r') as input_file:
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.responseReceived':
                url = e['params']['response']['url']
                ip_addr = e['params']['response']['remoteIPAddress']
                timing = e['params']['response']['timing']
                connect_ms = timing['connectEnd'] - timing['connectStart']
                ssl_ms = timing['sslEnd'] - timing['sslStart']
                print('{0} {1} {2} {3}'.format(url, ip_addr, connect_ms, ssl_ms))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('network_filename')
    args = parser.parse_args()
    Main()
