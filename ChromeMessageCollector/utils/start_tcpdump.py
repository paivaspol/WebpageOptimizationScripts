import phone_connection_utils

from argparse import ArgumentParser
from ConfigParser import ConfigParser

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('config_filename')
    argparser.add_argument('device', help='The device name e.g. Nexus_6')
    args = argparser.parse_args()

    # Setup the config filename
    config_reader = ConfigParser()
    config_reader.read(args.config_filename)

    # Get the device configuration.
    device_config = phone_connection_utils.get_device_configuration(config_reader, args.device)
    retval = -1
    while retval != 0:
        retval = phone_connection_utils.start_tcpdump(device_config)
