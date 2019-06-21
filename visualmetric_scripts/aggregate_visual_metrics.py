from argparse import ArgumentParser

import json
import os

SPEED_INDEX = 'speedindex'
AFT = 'aft'
FIRST_PAINT = 'first_paint'

choices = [ FIRST_PAINT, SPEED_INDEX, AFT ]

DICT_MAPPING = {
        SPEED_INDEX: 'SpeedIndex',
        AFT: 'LastVisualChange',
        FIRST_PAINT: 'FirstVisualChange',
}

def main(root_dir):
    for p in os.listdir(root_dir):
        visual_metrics_filename = os.path.join(root_dir, p, 'visual_metrics')
        if not os.path.exists(visual_metrics_filename):
            continue

        with open(visual_metrics_filename, 'r') as input_file:
            visual_metric_obj = json.load(input_file)

        output_line = p
        for k in choices:
            output_line += ' ' + str(visual_metric_obj[DICT_MAPPING[k]])
        print(output_line)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
