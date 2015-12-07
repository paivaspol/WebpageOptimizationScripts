from argparse import ArgumentParser

import os

def aggregate_data(root_dir):
    result = []
    header = None
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        full_path = os.path.join(path, 'low_utilization_times')
        if os.path.exists(full_path):
            print 'Processing: ' + full_path
            with open(full_path, 'rb') as input_file:
                header = input_file.readline() # header
                line = input_file.readline().strip().split()

                if len(result) < len(line):
                    # Initialize the result list
                    for i in range(0, len(line)):
                        result.append([])

                for i in range(0, len(line)):
                    result[i].append(float(line[i]))
    ratios = compute_ratio(result)            
    return result, ratios, header

def compute_ratio(result):
    total_times = result[0]
    ratios = []
    for i in range(1, len(result)):
        if len(ratios) < i:
            ratios.append([])
        for j in range(0, len(total_times)):
            ratios[i - 1].append(1.0 * result[i][j] / total_times[j])
    return ratios

def output_to_files(header, results, ratios, output_dir):
    extracted_header = extract_header(header)
    print 'extracted header: ' + str(extracted_header)
    print 'len header: {0} len results: {1} len ratios: {2}'.format(len(extracted_header), len(results), len(ratios))
    for i in range(0, len(extracted_header)):
        output_full_path = os.path.join(output_dir, 'threshold_' + extracted_header[i].replace('.', '_') + '.txt')
        with open(output_full_path, 'wb') as output_file:
            results[i].sort()
            for result in results[i]:
                output_file.write('{0}\n'.format(result))
        if i > 0:
            output_full_path = os.path.join(output_dir, 'threshold_' + extracted_header[i].replace('.', '_') + '_ratio.txt')
            with open(output_full_path, 'wb') as output_file:
                ratios[i - 1].sort()
                print 'len result: ' + str(len(ratios[i - 1]))
                for result in ratios[i - 1]:
                    output_file.write('{0}\n'.format(result))

def extract_header(header_str):
    return header.strip().split()[1:]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--output-dir', default='.')
    args = parser.parse_args()
    results, ratios, header = aggregate_data(args.root_dir)
    output_to_files(header, results, ratios, args.output_dir)
