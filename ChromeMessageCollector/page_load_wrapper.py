import subprocess

from argparse import ArgumentParser

NEXUS_6_CONFIG = '../phone_config/nexus6.cfg'
NEXUS_6 = 'Nexus_6'
NEXUS_5_CONFIG = '../phone_config/nexus5.cfg'
NEXUS_5 = 'Nexus_5'

def main(pages_file):
    with open(pages_file, 'rb') as input_file:
        counter = 0
        for raw_line in input_file:
            line = raw_line.strip()
            cmd = 'python get_chrome_messages.py {1} {2} {0} --output-dir ../../results/page_access_traces/'.format(line, NEXUS_5_CONFIG, NEXUS_5) 
            print 'Executing: ' + cmd
            subprocess.Popen(cmd, shell=True).wait()
            counter += 1
            if counter > 2:
                break

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('pages_file')
    args = parser.parse_args()
    main(args.pages_file)
