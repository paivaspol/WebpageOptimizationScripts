from argparse import ArgumentParser
from urlparse import urlparse
from collections import defaultdict

import os

def main(dependency_directory):
    pages = os.listdir(dependency_directory)
    for page in pages:
        dependency_filename = os.path.join(dependency_directory, page, 'dependency_tree.txt')
        dependencies = process_dependency_file(dependency_filename)
        ratios, histogram = find_domain_ratios(dependencies)
        print_results(page, ratios, histogram)

def print_results(page, ratios, histogram):
    print page
    sorted_ratios = sorted(ratios.iteritems(), key=lambda x: x[1], reverse=True)
    for url, ratio in sorted_ratios:
        print '\t{0} {1} {2}'.format(url, histogram[url], ratio)

def find_domain_ratios(dependencies):
    histogram = defaultdict(lambda: 0)
    for dep in dependencies:
        domain = urlparse(dep)
        histogram[domain.netloc] += 1
    return { k: (1.0 * v / len(dependencies)) for k, v in histogram.iteritems() }, histogram

def process_dependency_file(dependency_filename):
    dependencies = []
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[2]
            dep_type = line[4]
            if dep_type == 'Script' or \
                dep_type == 'Stylesheet' or \
                dep_type == 'Document':
                dependencies.append(url)
    return dependencies

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dependency_directory')
    args = parser.parse_args()
    main(args.dependency_directory)
