from argparse import ArgumentParser

import json
import os

def main(root_dir):
    for p in os.listdir(root_dir):
        if args.debug is not None and args.debug not in p:
            continue
        preloaded, all_objs = parse_file(os.path.join(root_dir, p, 'timings.txt'))
        preload_count = len(preloaded)
        all_objs_count = len(all_objs)
        fraction = 1.0 * preload_count / all_objs_count
        print '{0} {1} {2} {3}'.format(p, preload_count, all_objs_count, fraction)
        for p in preloaded:
            print '\t' + p


def parse_file(input_filename):
    with open(input_filename, 'rb') as input_file:
        all_objs = []
        preloaded = []
        for l in input_file:
            obj = json.loads(l.strip())
            if obj['preloaded']:
                preloaded.append(obj['url'])
            all_objs.append(obj['url'])
        return preloaded, all_objs

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--debug')
    args = parser.parse_args()
    main(args.root_dir)
