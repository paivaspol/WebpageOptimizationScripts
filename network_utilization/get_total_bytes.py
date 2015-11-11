import argparse

def get_total_bytes(bandwidth_filename):
    with open(bandwidth_filename, 'rb') as input_file:
        running_sum = 0
        for raw_line in input_file:
            counter, byte = raw_line.rstrip().split()
            running_sum += int(byte)
        print 'total bytes: ' + str(running_sum)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bandwidth_filename')
    args = parser.parse_args()
    get_total_bytes(args.bandwidth_filename)

