from argparse import ArgumentParser
from urlparse import urlparse

def main(server_side_log_file, dependency_file):
    duplicated_requests = find_duplicated_requests(server_side_log_file)
    dependencies = get_dependencies(dependency_file)
    print_dependencies_with_duplicated_requests(duplicated_requests, dependencies)

def print_dependencies_with_duplicated_requests(duplicated_requests, dependencies):
    # print duplicated_requests
    for dependency_entry in dependencies:
        dependency = dependency_entry[2]
        parsed_url = urlparse(dependency)
        if parsed_url.path in duplicated_requests:
            print '{0} {1} {2}'.format(dependency, dependency_entry[4], duplicated_requests[parsed_url.path])

def get_dependencies(dependency_file):
    with open(dependency_file, 'rb') as input_file:
        return [ line.strip().split() for line in input_file ]

def find_duplicated_requests(server_side_log_file):
    duplicated_requests = dict()
    with open(server_side_log_file, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            path = line[2]
            if path not in duplicated_requests:
                duplicated_requests[path] = 1
            else:
                duplicated_requests[path] += 1
    return { key: value for key, value in duplicated_requests.iteritems() if value >= 2 }

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('server_side_log_file')
    parser.add_argument('dependency_file')
    args = parser.parse_args()
    main(args.server_side_log_file, args.dependency_file)
