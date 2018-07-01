from argparse import ArgumentParser

import os
import shutil
import subprocess

def Main():
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    for p in os.listdir(args.root_dir):
        if 'nypost' not in p:
            continue
        print 'Processing: ' + p
        page_output_dir = os.path.join(args.output_dir, p)
        os.mkdir(page_output_dir)
        timeline_filename = os.path.join(args.root_dir, p)

        # First, we need to extract the images.
        raw_frames_dir = ExtractImagesFromTimeline(page_output_dir, timeline_filename)

        # Usage: python visualmetrics.py --dir nypost.com/ --timeline ../../results/webpage-complexity/adblocking/data/with_adblock_plus_fixed_25mbps_bw_10ms_rtt/chrome_tracing/nypost.com
        cmd = 'python visualmetrics.py --dir {0} --timeline {1}'.format(raw_frames_dir, timeline_filename)
        output = subprocess.check_output(cmd.split())
        with open(os.path.join(page_output_dir, 'visual_metrics'), 'w') as output_file:
            output_file.write(output)


def ExtractImagesFromTimeline(page_output_dir, timeline_filename):
    '''
    Extracts frames from the timeline and dump them into the output directory.
    '''
    raw_frames_dir = os.path.join(page_output_dir, 'raw_frames')
    print 'Extracting frames to ' + raw_frames_dir
    os.mkdir(raw_frames_dir)
    # Usage: ./trace_extract_snapshots.bash ../../results/webpage-complexity/adblocking/data/with_adblock_plus_fixed_25mbps_bw_10ms_rtt/chrome_tracing/nypost.com nypost.com
    cmd = './trace_extract_snapshots.bash {0} {1}'.format(timeline_filename, raw_frames_dir)
    subprocess.call(cmd.split())
    return raw_frames_dir


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    Main()
