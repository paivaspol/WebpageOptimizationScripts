import sys

from collections import defaultdict
from urlparse import urlparse

input_filename = sys.argv[1]

with open(input_filename, 'r') as input_file:
    histogram = defaultdict(int)
    for l in input_file:
        l = l.strip()
        if not l.startswith('http'):
            continue
        parsed_url = urlparse(l)
        histogram[parsed_url.netloc] += 1
        print parsed_url.netloc
    
    print '==========================================='
    print 'Histogram: '
    for k, v in histogram.iteritems():
        print k + ' ' + str(v)
