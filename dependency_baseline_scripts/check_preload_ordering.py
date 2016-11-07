from argparse import ArgumentParser

import constants
import os
import simplejson as json

def main(root_dir, dependency_dir):
    pages = os.listdir(root_dir)
    for page in pages:
        if 'abcnews.go.com' not in page:
            continue

        network_filename = os.path.join(root_dir, page, 'network_' + page)
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        if not (os.path.exists(network_filename) and \
                os.path.exists(dependency_filename)):
            continue
        
        dependency_set, dependency_list = get_dependency_list(dependency_filename)
        if check_preload_ordering(network_filename, dependency_set, dependency_list):
            print '{0} YES'.format(page)
        else:
            print '{0} NO'.format(page)

def check_preload_ordering(network_filename, dependency_set, dependency_list):
    counter = 0
    with open(network_filename, 'rb') as input_file:
        for raw_line in input_file:
            network_event = json.loads(raw_line.strip())
            if network_event[constants.METHOD] == 'Network.requestWillBeSent':
                url = network_event[constants.PARAMS][constants.REQUEST][constants.URL]
                if url in dependency_set and url != dependency_list[counter]:
                    print '{0} {1}'.format(url, dependency_list[counter])
                    return False
                elif url in dependency_set and url == dependency_list[counter]:
                    counter += 1
                    dependency_set.remove(url)
    return True

def get_dependency_list(dependency_filename):
    dependency_set = set()
    dependency_list = []
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            dependency_set.add(line[2])
            dependency_list.append(line[2])
    return dependency_set, dependency_list

        

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('dependency_dir')
    args = parser.parse_args()
    main(args.root_dir, args.dependency_dir)
