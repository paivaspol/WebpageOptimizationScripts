import subprocess
import signal # For timeout.
import os

from argparse import ArgumentParser
from time import sleep
from PageLoadException import PageLoadException

NEXUS_6_CONFIG = '../phone_config/nexus6.cfg'
NEXUS_6 = 'Nexus_6'
NEXUS_5_CONFIG = '../phone_config/nexus5.cfg'
NEXUS_5 = 'Nexus_5'
HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'

TIMEOUT = 2 * 60 # set to 2 minutes

def main(pages_file, num_repetitions, output_dir, use_caching_proxy, start_measurements):
    signal.signal(signal.SIGALRM, timeout_handler) # Setup the timeout handler
    pages = get_pages(pages_file)
    while len(pages) > 0:
        page = pages.pop(0)
        if use_caching_proxy:
            try:
                # Special Case for Populating the proxy cache.
                signal.alarm(TIMEOUT)
                load_page(page, -1, output_dir, False)
                signal.alarm(0) # Reset the alarm
            except PageLoadException as e:
                print 'Timeout for {0}-th load. Append to end of queue...'.format(i)
                pages.append(page)
        i = 0
        while i < num_repetitions:
            try:
                signal.alarm(TIMEOUT)
                load_page(page, i, output_dir, start_measurements)
                signal.alarm(0) # Reset the alarm
                i += 1
                iteration_path = os.path.join(output_dir, str(i - 1))
                if start_measurements:
                    stop_tcpdump_and_cpu_measurement(page.strip(), output_dir_run=iteration_path)
            except PageLoadException as e:
                print 'Timeout for {0}-th load. Append to end of queue...'.format(i)
                pages.append(page)
                break

def get_pages(pages_file):
    pages = []
    with open(pages_file, 'rb') as input_file:
        for raw_line in input_file:
            pages.append(raw_line)
    return pages

def load_page(raw_line, run_index, output_dir, start_measurements):
    base_output_dir = output_dir
    if not os.path.exists(base_output_dir):
        os.mkdir(base_output_dir)
    output_dir_run = os.path.join(base_output_dir, str(run_index))
    if not os.path.exists(output_dir_run):
        os.mkdir(output_dir_run)

    if start_measurements:
        start_cpu_measurement = 'python ./utils/start_cpu_measurement.py {0} {1}'.format(NEXUS_6_CONFIG, NEXUS_6)
        print 'Executing: ' + start_cpu_measurement
        subprocess.Popen(start_cpu_measurement, shell=True).wait()
        start_tcpdump = 'python ./utils/start_tcpdump.py {0} {1}'.format(NEXUS_6_CONFIG, NEXUS_6)
        subprocess.Popen(start_tcpdump, shell=True).wait()
    line = raw_line.strip()
    cmd = 'python get_chrome_messages.py {1} {2} {0} --output-dir {3}'.format(line, NEXUS_6_CONFIG, NEXUS_6, output_dir_run) 
    subprocess.Popen(cmd, shell=True).wait()

def stop_tcpdump_and_cpu_measurement(line, output_dir_run='.'):
    if WWW_PREFIX in line:
        url = line[len(HTTP_PREFIX) + len(WWW_PREFIX):]
    else:
        url = line[len(HTTP_PREFIX):]
    if '/' in url:
        url = url.replace('/', '_')
    output_directory = os.path.join(output_dir_run, url)
    cpu_measurement_output_filename = os.path.join(output_directory, 'cpu_measurement.txt')
    stop_cpu_measurement = 'python ./utils/stop_cpu_measurement.py {0} {1} {2}'.format(NEXUS_6_CONFIG, NEXUS_6, cpu_measurement_output_filename)
    subprocess.Popen(stop_cpu_measurement, shell=True).wait()
    pcap_output_filename = os.path.join(output_directory, 'output.pcap')
    stop_tcpdump = 'python ./utils/stop_tcpdump.py {0} {1} --output-dir {2} --no-sleep'.format(NEXUS_6_CONFIG, NEXUS_6, pcap_output_filename)
    subprocess.Popen(stop_tcpdump, shell=True).wait()

def timeout_handler(signum, frame):
    '''
    Handle the case where the page fails to load
    '''
    raise PageLoadException('Time\'s up for this load.')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_file')
    parser.add_argument('num_repetitions', type=int)
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--use-caching-proxy', default=False, action='store_true')
    parser.add_argument('--dont-start-measurements', default=False, action='store_true')
    args = parser.parse_args()
    start_measurements = not args.dont_start_measurements
    main(args.pages_file, args.num_repetitions, args.output_dir, args.use_caching_proxy, start_measurements)
