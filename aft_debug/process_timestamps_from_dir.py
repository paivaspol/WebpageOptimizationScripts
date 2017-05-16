import sys

if len(sys.argv) != 2:
    print 'Usage: ./process_timestamps.py [ts_filename]'
    sys.exit(1)

ts_filename = sys.argv[1]

with open(ts_filename, 'rb') as input_file:
    all_diffs = []
    prev_ts = -1
    for ts in input_file:
        if ts.strip().endswith('.jpg'):
            end_index = (len(ts) - len('.jpg'))
            ts = ts[0:end_index]
        ts = float(ts)
        if prev_ts != -1:
            diff = (ts - prev_ts)
            print diff
            all_diffs.append(diff)
        prev_ts = ts
    print 'Sum: ' + str(sum(all_diffs))
