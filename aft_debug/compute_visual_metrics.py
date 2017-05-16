from argparse import ArgumentParser

import os
import subprocess

def main(root_dir):
    for p in os.listdir(root_dir):
        plt = get_plt(os.path.join(root_dir, p, 'start_end_time_' + p))
        input_filename = os.path.join(root_dir, p, 'screen_record.mp4')
        cmd = 'python /Users/vaspol/Documents/research/MobileWebPageOptimization/binaries/visualmetrics/visualmetrics.py --start 2000 --end {0} -i {1} --full'.format((plt + 1500), input_filename)
        output = subprocess.check_output(cmd.split())
        print 'here: ' + output
        speedindex, aft = parse_visual_metrics(output)
        print '{0} {1} {2}'.format(p, speedindex, aft)
        break

def parse_visual_metrics(visual_metric_str):
    speedindex = -1
    aft = -1
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
    args = parser.parse_args()
    main(args.root_dir)
