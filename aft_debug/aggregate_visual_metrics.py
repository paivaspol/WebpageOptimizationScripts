from argparse import ArgumentParser

import os

def main(root_dir):
    for p in os.listdir(root_dir):
        visual_metrics_filename = os.path.join(root_dir, p, 'visual_metrics')
        if not os.path.exists(visual_metrics_filename):
            continue
        with open(visual_metrics_filename, 'rb') as input_file:
            v = -1
            dont_print = False
            for l in input_file:
                if l.startswith('Speed') and args.mode == 'SpeedIndex':
                    v = l.strip().split(':')[1].strip()
                    break
                elif l.startswith('First') and args.mode == 'FirstPaint':
                    v = int(l.strip().split(':')[1].strip()) - 2000
                    break
                elif l.startswith('Visual') and (args.mode == 'AFT' or args.mode == 'AFT_no_offset'):
                    tokens = l.strip().split(', ')
                    for t in tokens:
                        splitted_t = t.split('=')
                        try:
                            if splitted_t[1] == '100%':
                                if args.mode == 'AFT':
                                    v = int(splitted_t[0]) - 2000
                                else:
                                    v = int(splitted_t[0])
                                break
                        except:
                            dont_print = True
                            break
            if not dont_print:
                print '{0} {1}'.format(p, v)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('mode', choices=[ 'SpeedIndex', 'AFT', 'AFT_no_offset', 'FirstPaint' ])
    args = parser.parse_args()
    main(args.root_dir)
