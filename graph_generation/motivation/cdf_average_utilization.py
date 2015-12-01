# Graph: CDF across websites of average network utilization
# Output: sorted average network utilization of each website.
import os

from argparse import ArgumentParser

def generate_graph(root_dir):
    average_utilizations = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            # Skip empty directories
            continue

        filename = 'bandwidth.txt'
        full_path = os.path.join(path, filename)
        if not os.path.exists(full_path):
            continue
        with open(full_path, 'rb') as input_file:
            utilization_sum = 0.0
            num_intervals = 0
            for raw_line in input_file:
                line = raw_line.strip().split()
                utilization_sum += float(line[1])
                num_intervals += 1
            if num_intervals > 0:
                average_utilization = utilization_sum / num_intervals
                average_utilizations.append(average_utilization)
    average_utilizations.sort()
    return average_utilizations

def print_results(average_utilizations):
    for utilization in average_utilizations:
        print str(utilization)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir', help='Directory containing the bandwidth files')
    args = parser.parse_args()
    average_utilizations = generate_graph(args.root_dir)
    print_results(average_utilizations)

