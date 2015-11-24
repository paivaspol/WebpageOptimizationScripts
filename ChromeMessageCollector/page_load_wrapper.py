import subprocess
import os

from argparse import ArgumentParser
from time import sleep

NEXUS_6_CONFIG = '../phone_config/nexus6.cfg'
NEXUS_6 = 'Nexus_6'
NEXUS_5_CONFIG = '../phone_config/nexus5.cfg'
NEXUS_5 = 'Nexus_5'
HTTP_PREFIX = 'http://'

def main(pages_file):
    with open(pages_file, 'rb') as input_file:
        counter = 0
        for raw_line in input_file:
            start_tcpdump = 'python ./utils/start_tcpdump.py {0} {1}'.format(NEXUS_6_CONFIG, NEXUS_6)
            subprocess.Popen(start_tcpdump, shell=True).wait()
            line = raw_line.strip()
            cmd = 'python get_chrome_messages.py {1} {2} {0} --output-dir ../../results/alexa_200_page_loads/'.format(line, NEXUS_6_CONFIG, NEXUS_6) 
            subprocess.Popen(cmd, shell=True).wait()
            output_directory = os.path.join('../../results/alexa_200_page_loads/', line[len(HTTP_PREFIX):])
            output_filename = os.path.join(output_directory, 'output.pcap')
            stop_tcpdump = 'python ./utils/stop_tcpdump.py {0} {1} --output-dir {2}'.format(NEXUS_6_CONFIG, NEXUS_6, output_filename)
            subprocess.Popen(stop_tcpdump, shell=True).wait()
            counter += 1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_file')
    args = parser.parse_args()
    main(args.pages_file)
