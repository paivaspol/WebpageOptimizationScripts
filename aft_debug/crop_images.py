from argparse import ArgumentParser

from PIL import Image

import os

def main(directory, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for filename in os.listdir(directory):
        print filename
        if filename.startswith('ms_'):
            input_filename = os.path.join(directory, filename)
            output_filename = os.path.join(output_dir, filename)
            img = Image.open(input_filename)
            img2 = img.crop((0, 280, 1440, 2560))
            img2.save(output_filename)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    print 'Cropping images...'
    main(args.dir, args.output_dir)
