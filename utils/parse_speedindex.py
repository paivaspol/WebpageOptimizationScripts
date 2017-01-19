from argparse import ArgumentParser

import os

def main(root_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        speedindex_filename = os.path.join(root_dir, page)
        with open(speedindex_filename, 'rb') as input_file:
            cur_line = input_file.readline()
            aft = -1
            speedindex = -1
            perceptual_speedindex = -1
            for cur_line in input_file:
                temp_line = cur_line.strip()
                splitted_temp_line = temp_line.split(' ')
                if temp_line.startswith('Visually Complete: '):
                    aft = int(splitted_temp_line[len(splitted_temp_line) - 1])
                elif temp_line.startswith('Speed Index: '):
                    speedindex = float(splitted_temp_line[len(splitted_temp_line) - 1])
                elif temp_line.startswith('Perceptual Speed Index: '):
                    perceptual_speedindex = float(splitted_temp_line[len(splitted_temp_line) - 1])
            if aft > 0 and speedindex > 0 and perceptual_speedindex > 0:
                print '{0} {1} {2} {3}'.format(page, speedindex, perceptual_speedindex, aft)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)
