import sys
import shutil
import subprocess
import os

input_dir = sys.argv[1]
split_factor = int(sys.argv[2])
output_dir = sys.argv[3]

files = os.listdir(input_dir)
histogram = {}
for f in files:
    with open(os.path.join(input_dir, f), 'r') as input_file:
        num_lines = sum([ 1 for _ in input_file ])
        histogram[f] = num_lines
sorted_histogram = [ f[0] for f in sorted(histogram.iteritems(), key=lambda x: x[0], reverse=True) ]

result = {}
for i in xrange(0, split_factor):
    result[i] = []

for i, f in enumerate(sorted_histogram):
    bucket = i % split_factor
    result[bucket].append(f)


if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
os.mkdir(output_dir)

for i in xrange(0, split_factor):
    os.mkdir(os.path.join(output_dir, str(i)))
    for f in result[i]:
        src = os.path.join(input_dir, f)
        dst = os.path.join(output_dir, str(i), f)
        cmd = 'cp {0} {1}'.format(src, dst)
        subprocess.call(cmd.split())
