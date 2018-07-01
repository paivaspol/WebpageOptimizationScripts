import sys
import os
import http_record_pb2

from collections import defaultdict

root_dir = sys.argv[1]

histogram = defaultdict(int)
for d in os.listdir(root_dir):
    for f in os.listdir(os.path.join(root_dir, d)):
        with open(os.path.join(root_dir, d, f), 'r') as input_file:
            file_content = input_file.read()
            request_response = http_record_pb2.RequestResponse()
            request_response.ParseFromString(file_content)
            for h in request_response.response.header:
                if h.key == 'Content-Type' and h.value.startswith('image'):
                    histogram[h.value] += 1

for k, v in histogram.items():
    print '{0}: {1}'.format(k, v)

