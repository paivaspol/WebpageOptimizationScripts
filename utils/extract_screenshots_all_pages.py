import subprocess
import sys
import os

if len(sys.argv) < 4:
    print 'Usage: extract_screenshots_all_pages.py [root_dir] [iterations] [output_dir]'
    sys.exit(1)

root_dir = sys.argv[1]
iterations = int(sys.argv[2])
output_dir = sys.argv[3]

if not os.path.exists(output_dir):
    os.mkdir(output_dir)

if not os.path.exists(os.path.join(root_dir, 'chrome_tracing_0')):
    command = './parse_json_for_all_loads.sh {0} {1}'.format(root_dir, 4)
    subprocess.call(command.split())

for i in range(0, iterations):
    data_dir = os.path.join(root_dir, 'chrome_tracing_' + str(i))
    iter_output_dir = os.path.join(output_dir, str(i))
    if not os.path.exists(iter_output_dir):
        os.mkdir(iter_output_dir)
    command = 'python extract_screenshots.py {0} {1}'.format(data_dir, iter_output_dir)
    subprocess.call(command.split())

