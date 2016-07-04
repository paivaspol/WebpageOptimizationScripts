from argparse import ArgumentParser

import os

def main(root_dir):
    pages = os.listdir(root_dir)
    runtimes = []
    for page in pages:
        if args.mode == 'regular':
            html_parsing_runtime_filename = os.path.join(root_dir, page, 'html_parsing_runtime.txt')
            if not os.path.exists(html_parsing_runtime_filename):
                continue
            with open(html_parsing_runtime_filename, 'rb') as input_file:
                line = input_file.readline().strip().split()
                runtime = float(line[0])
                html_size = int(line[1])
                num_elements = int(line[2])
                runtimes.append((page, runtime, html_size, num_elements))
        elif args.mode == 'elements_hit':
            html_parsing_runtime_filename = os.path.join(root_dir, page, 'elements_stats.txt')
            if not os.path.exists(html_parsing_runtime_filename):
                continue
            with open(html_parsing_runtime_filename, 'rb') as input_file:
                page_runtime = -1
                page_element_stats = dict()
                for raw_line in input_file:
                    line = raw_line.strip().split()
                    runtime = float(line[0])
                    if page_runtime == -1:
                        page_runtime = runtime
                    element_type = line[1]
                    count = int(line[2])
                    page_element_stats[element_type] = count
                external_css = page_element_stats['external_css'] if 'external_css' in page_element_stats else 0
                src_attr = page_element_stats['src_attr'] if 'src_attr' in page_element_stats else 0
                inline_style = page_element_stats['inline_style'] if 'inline_style' in page_element_stats else 0
                runtimes.append((page, runtime, external_css, src_attr, inline_style))
    sorted_runtimes = sorted(runtimes, key=lambda x: x[1])
    for runtime in sorted_runtimes:
        if args.mode == 'regular':
            print '{0} {1} {2} {3}'.format(runtime[0], runtime[1], runtime[2], runtime[3])
        elif args.mode == 'elements_hit':
            print '{0} {1} {2} {3} {4}'.format(runtime[0], runtime[1], runtime[2], runtime[3], runtime[4])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('mode', choices=[ 'regular', 'elements_hit' ])
    args = parser.parse_args()
    main(args.root_dir)
