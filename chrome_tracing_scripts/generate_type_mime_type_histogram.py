from argparse import ArgumentParser
from collections import defaultdict

import constants
import os
import simplejson as json

MISSING_RESPONSE_TYPE = 'missing_response_type'
MISSING_MIME_TYPE = 'missing_mime_type'

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    result = defaultdict(lambda: 0)
    result_mime_types = set()
    for page in pages:
        network_filename = os.path.join(root_dir, page, 'network_' + page)
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not os.path.exists(network_filename) or \
            not os.path.exists(dependency_filename):
            continue
        dependencies = get_dependencies(dependency_filename)
        histogram, mime_type_set = get_histogram(network_filename, dependencies)
        update_keys(result, histogram)
        result_mime_types.update(mime_type_set)
    sorted_dict = sorted(result.iteritems(), key=lambda x: x[1], reverse=True)
    for key, value in sorted_dict:
        print '{0} {1}'.format(key, value)
    # for mime_type in result_mime_types:
    #     print mime_type

def get_dependencies(dependency_filename):
    dependencies = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            dependencies.add(line[2])
    return dependencies

def update_keys(a, b):
    for key, val in b.iteritems():
        a[key] += val

def get_histogram(network_filename, dependencies):
    histogram = defaultdict(lambda: 0)
    mime_type_set = set()
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip()
            network_event = json.loads(line)
            if network_event[constants.METHOD] == constants.NET_RESPONSE_RECEIVED:
                url = network_event[constants.PARAMS][constants.RESPONSE][constants.URL]
                if not url in dependencies:
                    continue
                if constants.TYPE not in network_event[constants.PARAMS]:
                    histogram[MISSING_RESPONSE_TYPE] += 1
                    continue
                if constants.MIME_TYPE not in network_event[constants.PARAMS][constants.RESPONSE]:
                    histogram[MISSING_MIME_TYPE] += 1
                    continue
                response_type = network_event[constants.PARAMS][constants.TYPE]
                mime_type = network_event[constants.PARAMS][constants.RESPONSE][constants.MIME_TYPE]
                pair = (response_type, mime_type)
                mime_type_set.add(mime_type)
                histogram[pair] += 1
    return histogram, mime_type_set

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
