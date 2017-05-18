import sys
import os

input_dir = sys.argv[1]

prev_ts = -1
for d in os.listdir(input_dir):
    ts = int(d[:len(d) - len('.jpg')])
    if prev_ts >= 0:
        print '{0} {1} {2}'.format(ts, prev_ts, ts - prev_ts)
    prev_ts = ts
