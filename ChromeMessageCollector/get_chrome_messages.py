import common_module
import json
import requests
import subprocess
import os
import websocket

from utils import phone_connection_utils

from argparse import ArgumentParser
from ConfigParser import ConfigParser   # Parsing configuration file.
from time import sleep
from RDPMessageCollector.ChromeRDPWebsocket import ChromeRDPWebsocket # The websocket

HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'
OUTPUT_DIR = None
PAGE_ID = None

def main(device_configuration, url):
    '''
    The main workflow of the script.
    '''
    output_directory = create_output_directory_for_url(url)
    print 'Stopping Chrome...'
    phone_connection_utils.stop_chrome(device_configuration)
    print 'Starting Chrome...'
    phone_connection_utils.start_chrome(device_configuration)
    
    cpu_chrome_running_on = phone_connection_utils.get_cpu_running_chrome(device_configuration)
    output_cpu_running_chrome(output_directory, cpu_chrome_running_on)

    # close_all_tabs(device_configuration)

    print 'Connected to Chrome...'
    got_debugging_url = False
    while not got_debugging_url:
        try:
            debugging_url, page_id = get_debugging_url(device_configuration)
            got_debugging_url = True
        except requests.exceptions.ConnectionError as e:
            pass
            
    device_configuration['page_id'] = page_id
    debugging_socket = ChromeRDPWebsocket(debugging_url, url, device_configuration, callback_on_page_done)

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
    
    final_url = common_module.escape_url(url)
    print 'base_dir: ' + base_dir + ' final_url: ' + final_url

    base_dir = os.path.join(base_dir, final_url)
    # Create the directory if the directory doesn't exist.
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    return base_dir

def callback_on_page_done(debugging_socket, network_messages, timeline_messages, device_configuration):
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
    start_end_time_filename = os.path.join(base_dir, 'start_end_time_' + final_url)
    with open(network_filename, 'wb') as output_file:
        for message in network_messages:
            output_file.write('{0}\n'.format(json.dumps(message)))
    # Output timeline objects
    if len(timeline_messages) > 0:
        with open(timeline_filename, 'wb') as output_file:
            for message in timeline_messages:
                output_file.write('{0}\n'.format(json.dumps(message)))
    # phone_connection_utils.stop_tcpdump(device_configuration)
    # phone_connection_utils.fetch_pcap(device_configuration, destination_directory=base_dir)
    
    # Get the start and end time of the execution
    start_time, end_time = get_start_end_time(debugging_url)
    with open(start_end_time_filename, 'wb') as output_file:
        output_file.write('{0} {1} {2}\n'.format(final_url, start_time, end_time))

    get_resource_tree(debugging_url)

    close_tab(device_configuration)

def get_start_end_time(debugging_url):
    # print 'debugging_url: ' + debugging_url
    start_time = None
    end_time = None
    while start_time is None or end_time is None or (start_time is not None and start_time <= 0) or (end_time is not None and end_time <= 0):
        try:
            ws = websocket.create_connection(debugging_url)
            navigation_starts = json.dumps({ "id": 6, "method": "Runtime.evaluate", "params": { "expression": "performance.timing.navigationStart", "returnByValue": True }})
            load_event_ends = json.dumps({ "id": 6, "method": "Runtime.evaluate", "params": { "expression": "performance.timing.loadEventEnd", "returnByValue": True }})
            # print 'navigation starts: ' + str(navigation_starts)
            ws.send(navigation_starts)
            nav_starts_result = json.loads(ws.recv())
            ws.send(load_event_ends)
            load_ends = json.loads(ws.recv())
            # print 'start time: ' + str(nav_starts_result)
            start_time = int(nav_starts_result['result']['result']['value'])
            end_time = int(load_ends['result']['result']['value'])
        except Exception as e:
            pass
        finally:
            ws.close()
    return start_time, end_time

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


def close_tab(device_configuration):
    '''
    Connects the client to the debugging socket.
    '''
    base_url = 'http://localhost:{0}/json/close/{1}'
    url = base_url.format(device_configuration[phone_connection_utils.ADB_PORT], device_configuration['page_id'])
    response = requests.get(url)
    # response_json = json.loads(response.text)
    print response.text

def close_all_tabs(device_configuration):
    '''
    Closes all the tabs in Chrome.
    '''
    base_url = 'http://localhost:{0}/json'
    url = base_url.format(device_configuration[phone_connection_utils.ADB_PORT])
    print 'base url: ' + url
    response = requests.get(url)
    print 'response: ' + str(response.text)
    response_json = json.loads(response.text)
    print 'response len: ' + str(len(response_json))
    for i in range(0, len(response_json)):
        response = response_json[i]
        page_id = response['id']
        base_url = 'http://localhost:{0}/json/close/{1}'
        url = base_url.format(device_configuration[phone_connection_utils.ADB_PORT], page_id)
        response = requests.get(url)

def get_debugging_url(device_configuration):
    '''
    Connects the client to the debugging socket.
    '''
    # print 'here (0)'
    base_url = 'http://localhost:{0}/json'
    url = base_url.format(device_configuration[phone_connection_utils.ADB_PORT])
    response = requests.get(url)
    # print 'response: ' + str(response.text)
    response_json = json.loads(response.text)
    page_id = response_json[0]['id']
    # Always use the 0th tab and return the connection to the debugging url.
    return response_json[0][phone_connection_utils.WEB_SOCKET_DEBUGGER_URL], page_id

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('config_filename')
    argparser.add_argument('device', help='The device name e.g. Nexus_6')
    argparser.add_argument('url', help='The URL to navigate to e.g. http://apple.com')
    argparser.add_argument('--output-dir', help='The output directory of the generated files', default=None)
    args = argparser.parse_args()

    # Setup the config filename
    config_reader = ConfigParser()
    config_reader.read(args.config_filename)
    OUTPUT_DIR = args.output_dir

    # Get the device configuration.
    device_config = phone_connection_utils.get_device_configuration(config_reader, args.device)
    main(device_config, args.url)
