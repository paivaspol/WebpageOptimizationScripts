from argparse import ArgumentParser
from multiprocessing import Pool

import itertools
import os
import subprocess

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    if args.debug:
        process_page(root_dir, 'android.livescore.com', output_dir)
    else:
        worker_pool = Pool(4)
        worker_pool.map(process_page_wrapper, itertools.izip( \
                                                itertools.repeat(root_dir), \
                                                os.listdir(root_dir), \
                                                itertools.repeat(output_dir)))

def process_page_wrapper(args):
    process_page(*args)

def process_page(root_dir, p, output_dir):
    plt = get_plt(os.path.join(root_dir, p, 'start_end_time_' + p))
    input_filename = os.path.join(root_dir, p, 'screen_record.mp4')
    page_output_dir = os.path.join(output_dir, p)
    if not os.path.exists(page_output_dir):
        os.mkdir(page_output_dir)
    cmd = 'python /Users/vaspol/Documents/research/MobileWebPageOptimization/binaries/visualmetrics/visualmetrics.py --start 2000 --end {0} -i {1} --full --dir {2}'.format((plt + 1500 + 2000), input_filename, page_output_dir)
    output = subprocess.check_output(cmd.split())
    with open(os.path.join(page_output_dir, 'visual_metrics'), 'wb') as output_file:
        output_file.write(output)


def parse_visual_metrics(visual_metric_str):
    speedindex = -1
    aft = -1
    splitted_visual_metric_str = visual_metric_str.strip().split('\n')
    for l in visual_metric_str:
        if l.startswith('Speed '):
            speedindex = l.split(':')[1].strip()
        elif l.startswith('Last Visual'):
            aft = l.split(':')[1].strip()
    return speedindex, aft

def get_plt(filename):
    with open(filename, 'rb') as input_file:
        _, start_time, end_time, _, _, _ = input_file.readline().strip().split()
        return int(end_time) - int(start_time)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    parser.add_argument('--debug', default=False, action='store_true')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
