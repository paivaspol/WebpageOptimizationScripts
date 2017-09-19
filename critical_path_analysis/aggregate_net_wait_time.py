from argparse import ArgumentParser

import os

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    for p in os.listdir(root_dir):
        if not os.path.exists(os.path.join(output_dir, p)):
            os.mkdir(os.path.join(output_dir, p))
        times = {}
        update_times(os.path.join(root_dir, p, 'data.txt'), times) # Hinted and preloaded
        update_times(os.path.join(root_dir, p, 'hinted_but_not_preloaded'), times) # Hinted but not preloaded
        update_times(os.path.join(root_dir, p, 'not_hinted'), times) # Not hinted
        with open(os.path.join(output_dir, p, 'net_wait_times'), 'wb') as output_file:
            for url, wait_time in times.iteritems():
                output_file.write('{0} {1}\n'.format(url, wait_time))

def update_times(filename, times):
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            wait_time = int(line[2]) # in microseconds
            url = line[0]
            times[url] = wait_time

if __name__  == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
