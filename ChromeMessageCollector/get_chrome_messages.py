import common_module
import json
import requests
import subprocess
import os
import websocket

from utils import phone_connection_utils
from utils import navigation_utils
from utils import chrome_utils

from argparse import ArgumentParser
from ConfigParser import ConfigParser   # Parsing configuration file.
from time import sleep
from RDPMessageCollector.ChromeRDPWebsocket import ChromeRDPWebsocket # The websocket
from RDPMessageCollector.ChromeRDPWithoutTracking import ChromeRDPWithoutTracing

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
OUTPUT_DIR = None
PAGE_ID = None

def main(device_configuration, url, disable_tracing, reload_page):
    '''
    The main workflow of the script.
    '''
    output_directory = create_output_directory_for_url(url)
    
    if device_configuration[phone_connection_utils.DEVICE_TYPE] != phone_connection_utils.DEVICE_MAC and \
        device_configuration[phone_connection_utils.DEVICE_TYPE] != phone_connection_utils.DEVICE_UBUNTU:
        cpu_chrome_running_on = phone_connection_utils.get_cpu_running_chrome(device_configuration)
        output_cpu_running_chrome(output_directory, cpu_chrome_running_on)

    # got_debugging_url = False
    # while not got_debugging_url:
    #     try:
    #         got_debugging_url = True
    #     except requests.exceptions.ConnectionError as e:
    #         pass
            
    debugging_url, page_id = chrome_utils.get_debugging_url(device_configuration)
    print 'Connected to Chrome...'
    device_configuration['page_id'] = page_id
    user_agent_str = None
    if phone_connection_utils.USER_AGENT in device_configuration:
        user_agent_str = device_configuration[phone_connection_utils.USER_AGENT]

    if disable_tracing:
        chrome_rdp_object_without_tracing = ChromeRDPWithoutTracing(debugging_url, url, user_agent_str)
        start_time, end_time = chrome_rdp_object_without_tracing.navigate_to_page(url, reload_page)
        print str((start_time, end_time)) + ' ' + str((end_time - start_time))
        escaped_url = common_module.escape_page(url)
        write_page_start_end_time(escaped_url, output_directory, start_time, end_time)
    else:
        debugging_socket = ChromeRDPWebsocket(debugging_url, url, device_configuration, reload_page, user_agent_str, callback_on_page_done)

def output_cpu_running_chrome(output_directory, cpu_id):
    '''
    Outputs the CPU id that is running chrome.
    '''
    cpu_running_chrome_filename = os.path.join(output_directory, 'cpu_running_chrome.txt')
    with open(cpu_running_chrome_filename, 'wb') as output_file:
        output_file.write(cpu_id)

def create_output_directory_for_url(url):
    '''
    Creates an output directory for the url
    '''
    base_dir = ''
    if OUTPUT_DIR is not None:
        base_dir = os.path.join(base_dir, OUTPUT_DIR)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
    
    final_url = common_module.escape_page(url)

    base_dir = os.path.join(base_dir, final_url)
    # Create the directory if the directory doesn't exist.
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    return base_dir

def callback_on_page_done(debugging_socket, network_messages, timeline_messages, original_request_ts, load_event_ts, device_configuration):
    '''
    Sets up the call back once the page is done loading.
    '''
    print 'Page load done.' 
    # First, close the connection.
    debugging_socket.close_connection()
    url = debugging_socket.get_navigation_url()
    debugging_url = debugging_socket.get_debugging_url()
    final_url = common_module.escape_url(url)
    base_dir = create_output_directory_for_url(url)
    
    network_filename = os.path.join(base_dir, 'network_' + final_url)
    timeline_filename = os.path.join(base_dir, 'timeline_' + final_url)
    with open(network_filename, 'wb') as output_file:
        for message in network_messages:
            output_file.write('{0}\n'.format(json.dumps(message)))
    # Output timeline objects
    if len(timeline_messages) > 0:
        with open(timeline_filename, 'wb') as output_file:
            for message in timeline_messages:
                output_file.write('{0}\n'.format(json.dumps(message)))
    # Get the start and end time of the execution
    start_time, end_time = navigation_utils.get_start_end_time(debugging_url)
    write_page_start_end_time(final_url, base_dir, start_time, end_time, original_request_ts, load_event_ts)
    # get_resource_tree(debugging_url)
    chrome_utils.close_tab(device_configuration, device_configuration['page_id'])

def write_page_start_end_time(escaped_url, base_dir, start_time, end_time, original_request_ts=-1, load_event_ts=-1):
    start_end_time_filename = os.path.join(base_dir, 'start_end_time_' + escaped_url)
    with open(start_end_time_filename, 'wb') as output_file:
        output_file.write('{0} {1} {2} {3} {4}\n'.format(escaped_url, start_time, end_time, original_request_ts, load_event_ts))

def get_resource_tree(debugging_url):
    try:
        ws = websocket.create_connection(debugging_url)
        get_resource_tree = json.dumps({ "id": 6, "method": "Page.getResourceTree", "params": { }})
        # print 'navigation starts: ' + str(navigation_starts)
        ws.send(get_resource_tree)
        resource_tree = json.loads(ws.recv())
        # print 'start time: ' + str(nav_starts_result)
        print resource_tree
    except Exception as e:
        pass
    finally:
        ws.close()

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('config_filename')
    argparser.add_argument('device', help='The device name e.g. Nexus_6')
    argparser.add_argument('url', help='The URL to navigate to e.g. http://apple.com')
    argparser.add_argument('--output-dir', help='The output directory of the generated files', default=None)
    argparser.add_argument('--disable-tracing', default=False, action='store_true')
    argparser.add_argument('--reload-page', default=False, action='store_true')
    args = argparser.parse_args()

    # Setup the config filename
    config_reader = ConfigParser()
    config_reader.read(args.config_filename)
    OUTPUT_DIR = args.output_dir

    # Get the device configuration.
    device_config = phone_connection_utils.get_device_configuration(config_reader, args.device)
    main(device_config, args.url, args.disable_tracing, args.reload_page)
