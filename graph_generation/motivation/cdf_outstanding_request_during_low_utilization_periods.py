# Graph: CDF across low utilization periods of the number of outstanding requests.
# Low utilization periods are defined in the variable THRESHOLD below.
from argparse import ArgumentParser

import os

THRESHOLD = 0.01

def generate_graph_data(root_dir):
    result = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) <= 0:
            # Skip empty directories
            continue
        
        filename = 'outstanding_requests.txt'
        full_path = os.path.join(path, filename)
        if not os.path.exists(full_path):
            continue

        with open(full_path, 'rb') as input_file:
            for raw_line in input_file:
                line = raw_line.strip().split()
                utilization = float(line[3])
                outstanding_requests = int(line[4])
                if utilization <= THRESHOLD:
                    # Add the number of outstanding requests when the utilization is lower than the threshold.
                    result.append(outstanding_requests)
    result.sort()
    return result

def print_results(results):
    for outstanding_requests in results:
        print str(outstanding_requests)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    results = generate_graph_data(args.root_dir)
    print_results(results)
