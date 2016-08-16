import sys
import os

if len(sys.argv) < 2:
    print 'Usage: get_timestamps.py [directory]'
    sys.exit(1)

directory = sys.argv[1]

timestamps = os.listdir(directory)
timestamps.sort()

for ts in timestamps:
    if os.path.isdir(os.path.join(directory, ts)):
        print ts
