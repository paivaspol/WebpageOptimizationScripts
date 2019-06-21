from argparse import ArgumentParser
from multiprocessing import Pool

import os
import shutil
import subprocess

def Main():
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.mkdir(args.output_dir)

    pool = Pool()

    for i, p in enumerate(os.listdir(args.root_dir)):
        print('Processing: ' + p)
        page_output_dir = os.path.join(args.output_dir, p)
        os.mkdir(page_output_dir)
        timeline_filename = os.path.join(args.root_dir, p)
        # ComputeVisualMetricsForPage(timeline_filename, page_output_dir)
        pool.apply_async(ComputeVisualMetricsForPage, args=(timeline_filename,
            page_output_dir))

    pool.close()
    pool.join()


def ComputeVisualMetricsForPage(timeline_filename, page_output_dir):
    # First, we need to extract the images.
    raw_frames_dir = ExtractImagesFromTimeline(timeline_filename,
            page_output_dir)

    # Usage: python visualmetrics.py --dir nypost.com/ --timeline ../../results/webpage-complexity/adblocking/data/with_adblock_plus_fixed_25mbps_bw_10ms_rtt/chrome_tracing/nypost.com
    cmd = 'python visualmetrics.py --dir {0} --timeline {1} --json'.format(raw_frames_dir, timeline_filename)
    print(cmd)
    try:
        output = subprocess.check_output(cmd.split())
        with open(os.path.join(page_output_dir, 'visual_metrics'), 'w') as output_file:
            output_file.write(output)
    except Exception as e:
        print(e)
        pass



def ExtractImagesFromTimeline(timeline_filename, page_output_dir):
    '''
    Extracts frames from the timeline and dump them into the output directory.
    '''
    raw_frames_dir = os.path.join(page_output_dir, 'raw_frames')
    print('Extracting frames to ' + raw_frames_dir)
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
