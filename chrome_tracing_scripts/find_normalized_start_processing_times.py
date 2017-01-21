from argparse import ArgumentParser

import common_module
import os

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        processing_filename = os.path.join(root_dir, page, 'processing_time.txt')
        normalized_processing_times = compute_normalized_processing_times(processing_filename, page)
        output_to_file(output_dir, page, normalized_processing_times)

def output_to_file(output_dir, page, times):
    if not os.path.exists(os.path.join(output_dir, page)):
        os.mkdir(os.path.join(output_dir, page))

    output_filename = os.path.join(output_dir, page, 'normalized_start_processing_time.txt')
    with open(output_filename, 'wb') as output_file:
        for url_tuple, start_processing in times:
            output_file.write('{0} {1} {2}\n'.format(url_tuple[0], url_tuple[1], start_processing))

def compute_normalized_processing_times(processing_time_filename, page):
    root_html_start_processing_time = -1
    processing_times = dict()
    with open(processing_time_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            object_id = line[1]
            start_processing_time = int(line[2])
            if common_module.escape_page(url) == page:
                root_html_start_processing_time = start_processing_time

            if url not in processing_times:
                processing_times[(url, object_id)] = start_processing_time
            else:
                processing_times[(url, object_id)] = min(start_processing_time, processing_times[url])

    # Normalize
    print 'start_processing: ' + str(root_html_start_processing_time)
    return sorted([ (url_tuple, (start - root_html_start_processing_time)) for url_tuple, start in processing_times.iteritems() ], key=lambda x: x[1])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
