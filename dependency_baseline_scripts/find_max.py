import sys
import numpy

f = sys.argv[1]

with open(f, 'rb') as input_file:
    all_max = []
    for raw_line in input_file:
        if raw_line.startswith('#'):
            continue
        line = raw_line.strip().split()
        page_max = max(int(line[2]), int(line[4]), int(line[6]))
        print line[0] + ' ' + str(page_max)
        all_max.append(page_max)
    total_max = max(all_max)
    # print 'total_max: ' + str(total_max)
    # print 'median_max: ' + str(numpy.median(all_max))

