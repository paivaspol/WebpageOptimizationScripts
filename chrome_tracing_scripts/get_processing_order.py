import sys

if len(sys.argv) != 2:
    print 'Usage: get_processing_order.py [processing_filename]'
    sys.exit(1)

processing_time_filename = sys.argv[1]

processing_order = []
seen_urls = set()
with open(processing_time_filename, 'rb') as input_file:
    for raw_line in input_file:
        line = raw_line.strip().split()
        url = line[0]
        start_proc_time = int(line[2])
        if url not in seen_urls:
            processing_order.append((url, start_proc_time))
            seen_urls.add(url)

sorted_processing_order = sorted(processing_order, key=lambda x: x[1])

for u, t in sorted_processing_order:
    print u
