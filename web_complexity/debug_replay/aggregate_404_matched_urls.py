from argparse import ArgumentParser
from urllib.parse import urlparse

import os

def Main():
    for d in os.listdir(args.root_dir):
        with open(os.path.join(args.root_dir, d), 'r') as input_file:
            for l in input_file:
                l = l.strip().split()
                if int(l[-1]) == 404 and l[1] == '[NO_MATCH]':
                    parsed_url = urlparse(l[0])
                    len_path = len(parsed_url.path + ';' + parsed_url.params)
                    frac = 1.0 * int(l[4]) / len_path
                    print('{0} {1} {2} {3} {4} {5} {6}'.format(l[0], l[1], l[3], l[4],
                        len_path, l[5], frac))

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
