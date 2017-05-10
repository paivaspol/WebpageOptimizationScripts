from argparse import ArgumentParser
from multiprocessing import Pool

import os
import subprocess

NUM_CPU = 4

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pool = Pool(NUM_CPU)
    pool.map(run_script, os.listdir(args.root_dir))

def run_script(p):
    snapshot_dir = os.path.join(args.root_dir, p)
    final_output_dir = os.path.join(args.output_dir, p)
    if not os.path.exists(final_output_dir):
        os.mkdir(final_output_dir)
    command = './trace_extract_snapshots.bash {0} {1}'.format(snapshot_dir, final_output_dir)
    subprocess.call(command.split())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
