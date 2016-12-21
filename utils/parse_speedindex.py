from argparse import ArgumentParser

import os

def main(speedindex_filename, root_dir):
    pages = set(os.listdir(root_dir))
    cur_page = None
    with open(speedindex_filename, 'rb') as input_file:
        cur_line = input_file.readline()
        while cur_line != '':
            page = cur_line.strip()

            if page in pages:
                aft = -1
                speedindex = -1
                perceptual_speedindex = -1
                for i in range(0, 9):
                    temp_line = input_file.readline().strip()
                    if i == 0 and not temp_line.startswith('First Visual Change'):
                        while cur_line != '\n':
                            cur_line = input_file.readline()
                        break
                    splitted_temp_line = temp_line.split(' ')
                    if temp_line.startswith('Visually Complete: '):
                        aft = int(splitted_temp_line[len(splitted_temp_line) - 1])
                    elif temp_line.startswith('Speed Index: '):
                        speedindex = float(splitted_temp_line[len(splitted_temp_line) - 1])
                    elif temp_line.startswith('Perceptual Speed Index: '):
                        perceptual_speedindex = float(splitted_temp_line[len(splitted_temp_line) - 1])
                if aft > 0 and speedindex > 0 and perceptual_speedindex > 0:
                    print '{0} {1} {2} {3}'.format(page, speedindex, perceptual_speedindex, aft)
            cur_line = input_file.readline()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('speedindex_filename')
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.speedindex_filename, args.root_dir)
