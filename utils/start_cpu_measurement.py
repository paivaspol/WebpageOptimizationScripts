import phone_connection_utils

from argparse import ArgumentParser
from ConfigParser import ConfigParser

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('config_filename')
    args = argparser.parse_args()

    # Setup the config filename
    config_reader = ConfigParser()
    config_reader.read(args.config_filename)
    # Get the device configuration.
    device_config = phone_connection_utils.get_device_configuration(config_reader, args.device)
    phone_connection_utils.toggle_cpu_measurement(device_config)
