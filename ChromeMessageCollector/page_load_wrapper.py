import subprocess
import requests
import signal # For timeout.
import os
import simplejson

from argparse import ArgumentParser
from ConfigParser import ConfigParser
from time import sleep
from PageLoadException import PageLoadException

from utils import phone_connection_utils
from utils import chrome_utils

NEXUS_6_CONFIG = '../device_config/nexus6.cfg'
NEXUS_6 = 'Nexus_6'
NEXUS_6_2_CONFIG = '../device_config/nexus6_2.cfg'
NEXUS_6_2 = 'Nexus_6_2'
NEXUS_5_CONFIG = '../device_config/nexus5.cfg'
NEXUS_5 = 'Nexus_5'
MAC_CONFIG = '../device_config/mac.cfg'
MAC = 'mac'
HTTP_PREFIX = 'http://'
HTTPS_PREFIX = 'https://'
WWW_PREFIX = 'www.'

TIMEOUT = 5 * 60 # set to 5 minutes
PAUSE = 2
BUFFER_FOR_TRACE = 5

def main(pages_file, num_repetitions, output_dir, use_caching_proxy, start_measurements, device, disable_tracing):
    signal.signal(signal.SIGALRM, timeout_handler) # Setup the timeout handler
    pages = get_pages(pages_file)
    initialize_browser(device)
    while len(pages) > 0:
        page = pages.pop(0)
        print 'page: ' + page
        if use_caching_proxy:
            try:
                # Special Case for Populating the proxy cache.
                signal.alarm(TIMEOUT)
                load_page(page, -1, output_dir, False, device, True)
                signal.alarm(0) # Reset the alarm
            except PageLoadException as e:
                print 'Timeout for {0}-th load. Append to end of queue...'.format(i)
                pages.append(page)
        i = 0
        while i < num_repetitions:
            try:
                signal.alarm(TIMEOUT)
                load_page(page, i, output_dir, start_measurements, device, disable_tracing)
                if not disable_tracing:
                    # Kill the browser.
                    sleep(BUFFER_FOR_TRACE)
                    initialize_browser(device)
                signal.alarm(0) # Reset the alarm
                i += 1
                iteration_path = os.path.join(output_dir, str(i - 1))
                if start_measurements:
                    stop_tcpdump_and_cpu_measurement(page.strip(), device, output_dir_run=iteration_path)
            except PageLoadException as e:
                print 'Timeout for {0}-th load. Append to end of queue...'.format(i)
                # Kill the browser and append a page.
                initialize_browser(device)
                pages.append(page)
                break
            sleep(PAUSE)
    # shutdown_browser(device)

def get_pages(pages_file):
    pages = []
    with open(pages_file, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            pages.append(line[len(line) - 1])
    return pages

def initialize_browser(device):
    # Get the device configuration
    device, device_config = get_device_config(device)
    config_reader = ConfigParser()
    config_reader.read(device_config)
    device_config_obj = phone_connection_utils.get_device_configuration(config_reader, device)
    phone_connection_utils.wake_phone_up(device_config_obj)
    print 'Stopping Chrome...'
    phone_connection_utils.stop_chrome(device_config_obj)
    print 'Starting Chrome...'
    phone_connection_utils.start_chrome(device_config_obj)
    closed_tabs = False
    while not closed_tabs:
        try:
            chrome_utils.close_all_tabs(device_config_obj)
            closed_tabs = True
        except requests.exceptions.ConnectionError as e:
            pass

def shutdown_browser(device):
    device, device_config = get_device_config(device)
    config_reader = ConfigParser()
    config_reader.read(device_config)
    device_config_obj = phone_connection_utils.get_device_configuration(config_reader, device)
    print 'Stopping Chrome...'
    phone_connection_utils.stop_chrome(device_config_obj)

def load_page(raw_line, run_index, output_dir, start_measurements, device, disable_tracing):
    # Create necessary directories
    base_output_dir = output_dir
    if not os.path.exists(base_output_dir):
        os.mkdir(base_output_dir)
    output_dir_run = os.path.join(base_output_dir, str(run_index))
    if not os.path.exists(output_dir_run):
        os.mkdir(output_dir_run)
    
    # Get the device configuration
    device, device_config = get_device_config(device)
    if start_measurements:
        start_cpu_measurement = 'python ./utils/start_cpu_measurement.py {0} {1}'.format(device_config, device)
        print 'Executing: ' + start_cpu_measurement
        subprocess.Popen(start_cpu_measurement, shell=True).wait()
        start_tcpdump = 'python ./utils/start_tcpdump.py {0} {1}'.format(device_config, device)
        subprocess.Popen(start_tcpdump, shell=True).wait()
    line = raw_line.strip()
    cmd = 'python get_chrome_messages.py {1} {2} {0} --output-dir {3}'.format(line, device_config, device, output_dir_run) 
    if disable_tracing:
        cmd += ' --disable-tracing'
    if run_index > 0:
        cmd += ' --reload-page'
    subprocess.Popen(cmd, shell=True).wait()

def stop_tcpdump_and_cpu_measurement(line, device, output_dir_run='.'):
    url = escape_url(line)
    device, device_config = get_device_config(device)
    output_directory = os.path.join(output_dir_run, url)
    cpu_measurement_output_filename = os.path.join(output_directory, 'cpu_measurement.txt')
    stop_cpu_measurement = 'python ./utils/stop_cpu_measurement.py {0} {1} {2}'.format(device_config, device, cpu_measurement_output_filename)
    subprocess.Popen(stop_cpu_measurement, shell=True).wait()
    pcap_output_filename = os.path.join(output_directory, 'output.pcap')
    stop_tcpdump = 'python ./utils/stop_tcpdump.py {0} {1} --output-dir {2} --no-sleep'.format(device_config, device, pcap_output_filename)
    subprocess.Popen(stop_tcpdump, shell=True).wait()

def escape_url(url):
    if url.endswith('/'):
        url = url[:len(url) - 1]
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url.replace('/', '_')

def timeout_handler(signum, frame):
    '''
    Handle the case where the page fails to load
    '''
    raise PageLoadException('Time\'s up for this load.')

def get_device_config(device):
    if device == NEXUS_6:
        return NEXUS_6, NEXUS_6_CONFIG
    if device == NEXUS_6_2:
        return NEXUS_6_2, NEXUS_6_2_CONFIG
    elif device == NEXUS_5:
        return NEXUS_5, NEXUS_5_CONFIG
    elif device == MAC:
        return MAC, MAC_CONFIG

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_file')
    parser.add_argument('num_repetitions', type=int)
    parser.add_argument('--output-dir', default='.')
    parser.add_argument('--use-caching-proxy', default=False, action='store_true')
    parser.add_argument('--dont-start-measurements', default=False, action='store_true')
    parser.add_argument('--use-device', default=NEXUS_6_2)
    parser.add_argument('--disable-tracing', default=False, action='store_true')
    args = parser.parse_args()
    start_measurements = not args.dont_start_measurements
    main(args.pages_file, args.num_repetitions, args.output_dir, args.use_caching_proxy, start_measurements, args.use_device, args.disable_tracing)
