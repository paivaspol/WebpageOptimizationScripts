import sys

if len(sys.argv) != 3:
    print 'Usage: ./process_timestamps.py [ts_filename] [limit]'
    sys.exit(1)

ts_filename = sys.argv[1]
limit = float(sys.argv[2])

with open(ts_filename, 'rb') as input_file:
    all_diffs = []
    prev_ts = -1
    cumulative_sum = 0
    for ts in input_file:
        ts = float(ts)
        if prev_ts != -1:
            diff = (ts - prev_ts) / 1000
            cumulative_sum += diff
            if cumulative_sum > limit:
                break
            print diff
        prev_ts = ts
    print 'Sum: ' + str(cumulative_sum)
