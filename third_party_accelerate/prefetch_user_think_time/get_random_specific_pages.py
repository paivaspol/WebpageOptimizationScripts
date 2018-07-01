from urlparse import urlparse

import random
import sys
import os

root_dir = sys.argv[1]

for f in os.listdir(root_dir):
    print 'processing: ' + f
    with open(os.path.join(root_dir, f), 'r') as input_file:
        all_urls = [ x.strip() for x in input_file.readlines() ]
        selected = random.sample(all_urls, 1)[0]
        parsed_selected = urlparse(selected)
        while f not in parsed_selected.netloc:
            selected = random.sample(all_urls, 1)[0]
            parsed_selected = urlparse(selected)
        print selected
