from argparse import ArgumentParser

import os
import subprocess
import common_module

def main(root_dir, output_dir):
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        cpu_utilization_filename = os.path.join(path, 'cpu_measurement.txt')
        cpu_running_chrome_filename = os.path.join(path, 'cpu_running_chrome.txt')
        url = common_module.extract_url_from_path(path)
        interval_filename = os.path.join(path, 'start_end_time_' + url)
        escaped_path = url if not url.endswith('_') else url[:len(url) - 1]
        page_output_dir = os.path.join(output_dir, escaped_path)
        if not os.path.exists(page_output_dir):
            os.mkdir(page_output_dir)
        command = 'python find_cpu_utilization.py {0} {1} {2}'.format(cpu_utilization_filename, interval_filename, page_output_dir, cpu_running_chrome_filename)
        subprocess.call(command, shell=True)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
