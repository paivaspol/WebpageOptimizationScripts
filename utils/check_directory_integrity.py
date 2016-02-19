from argparse import ArgumentParser

import os

def evaluate_dir(root_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        elif 0 < len(filenames) < 5:
            print path + ' ' + str(filenames)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    evaluate_dir(args.root_dir)

