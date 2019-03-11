from argparse import ArgumentParser

import common
import json

def Main():
    with open(args.page_info, 'r') as input_file:
        info = json.load(input_file)

    for i in info:
        url = common.escape_page(i['url'])
        onload = i['onLoad']
        print('{0} {1}'.format(url, onload))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('page_info')
    args = parser.parse_args()
    Main()
