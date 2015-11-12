import subprocess

from argparse import ArgumentParser

def main(pages_file):
    with open(pages_file, 'rb') as input_file:
        counter = 0
        for raw_line in input_file:
            line = raw_line.strip()
            cmd = 'python get_chrome_messages.py ../phone_config/nexus6.cfg Nexus_6 {0} --output-dir ../../results/page_access_traces/'.format(line) 
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
