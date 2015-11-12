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
OUTPUT_DIR = None

def main(device_configuration, url):
    '''
    The main workflow of the script.
    '''
    print 'Stopping tcpdump...'
    phone_connection_utils.stop_tcpdump(device_configuration, sleep_before_kill=False)
    print 'Starting tcpdump...'
    phone_connection_utils.start_tcpdump(device_configuration)
    print 'Stopping Chrome...'
    phone_connection_utils.stop_chrome(device_configuration)
    print 'Starting Chrome...'
    phone_connection_utils.start_chrome(device_configuration)

    print 'Connected to Chrome...'
    debugging_url = get_debugging_url(device_configuration)
    debugging_socket = ChromeRDPWebsocket(debugging_url, url, device_configuration, callback_on_page_done)

def callback_on_page_done(debugging_socket, network_messages, timeline_messages, device_configuration):
    '''
    Sets up the call back once the page is done loading.
    '''
    print 'Page load done.' 
    # First, close the connection.
    debugging_socket.close_connection()
    url = debugging_socket.get_navigation_url()
    base_dir = ''
    if OUTPUT_DIR is not None:
        base_dir = os.path.join(base_dir, OUTPUT_DIR)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)

    base_dir = os.path.join(base_dir, url[len(HTTP_PREFIX):])
    # Create the directory if the directory doesn't exist.
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)

    network_filename = os.path.join(base_dir, 'network_' + url[len(HTTP_PREFIX):])
    timeline_filename = os.path.join(base_dir, 'timeline_' + url[len(HTTP_PREFIX):])
    with open(network_filename, 'wb') as output_file:
        for message in network_messages:
            output_file.write('{0}\n'.format(json.dumps(message)))
    with open(timeline_filename, 'wb') as output_file:
        for message in timeline_messages:
            output_file.write('{0}\n'.format(json.dumps(message)))
    phone_connection_utils.stop_tcpdump(device_configuration)
    phone_connection_utils.fetch_pcap(device_configuration, destination_directory=base_dir)

def get_debugging_url(device_configuration):
    '''
    Connects the client to the debugging socket.
    '''
    base_url = 'http://localhost:{0}/json'
    url = base_url.format(device_configuration[phone_connection_utils.ADB_PORT])
    response = requests.get(url)
    response_json = json.loads(response.text)
    # Always use the 0th tab and return the connection to the debugging url.
    return response_json[0][phone_connection_utils.WEB_SOCKET_DEBUGGER_URL]


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

