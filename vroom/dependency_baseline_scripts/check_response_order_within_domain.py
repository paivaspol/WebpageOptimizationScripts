from argparse import ArgumentParser
from urlparse import urlparse
from collections import defaultdict

import os

def main(extended_waterfall_dir, dependency_dir):
    pages = os.listdir(extended_waterfall_dir)
    for page in pages:
        if args.website is not None and args.website not in page:
            continue
    
        dependency_filename = os.path.join(dependency_dir, page, 'dependency_tree.txt')
        response_received_filename = os.path.join(extended_waterfall_dir, page, 'ResourceReceiveResponse.txt')
        finish_filename = os.path.join(extended_waterfall_dir, page, 'ResourceFinish.txt')
        
        # First, get the ordering from the dependency file.
        per_domain_ordering, dependencies = get_ordering_from_dependency_file(dependency_filename)

        # Second, get the ordering from the response received file
        per_domain_response_ordering = get_ordering_from_response_file(response_received_filename, dependencies)
        per_domain_last_byte_ordering = get_ordering_from_response_file(finish_filename, dependencies)

        # Third, check the ordering.
        print page
        check_ordering(per_domain_ordering, per_domain_response_ordering, per_domain_last_byte_ordering)

def check_ordering(dependency_ordering, response_ordering, finish_ordering):
    for domain in dependency_ordering:
        if domain in response_ordering:
            passed = True
            response_order = response_ordering[domain]
            finish_order = finish_ordering[domain]
            dependency_order = dependency_ordering[domain]
            same_length = len(response_order) == len(dependency_order)
            for i in range(0, min(len(dependency_ordering), len(response_order))):
                if response_order[i][0] != dependency_order[i]:
                    passed = False
                    break
            if passed:
                print '\t{0}: DEPENDENCY ORDERING PASSED'.format(domain)
            else:
                print '\t{0}: DEPENDENCY ORDERING FAILED'.format(domain)
                print '\tdep order: ' + str(dependency_order)
                print '\tresponse order: ' + str(response_order)

            if not same_length:
                print '\t\tWarning: different length. response len: {0} dependency len: {1}'.format(len(response_order), len(dependency_order))

            passed = True
            for i in range(0, min(len(finish_order), len(response_order)) - 1):
                last_byte_ts = finish_order[i][1]
                next_response_first_byte_ts = response_order[i + 1][1]
                if next_response_first_byte_ts < last_byte_ts:
                    passed = False
                    break
            
            if passed:
                print '\t{0}: TEMPORAL ORDERING PASSED'.format(domain)
            else:
                print '\t{0}: TEMPORAL ORDERING FAILED'.format(domain)

def get_ordering_from_dependency_file(dependency_filename):
    per_domain_ordering = defaultdict(list)
    dependencies = set()
    with open(dependency_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            dependency_url = line[2]
            dep_type = line[4]
            parsed_url = urlparse(dependency_url)
            if dep_type == 'Script' or dep_type == 'Stylesheet' or dep_type == 'Document':
                per_domain_ordering[parsed_url.netloc].append(dependency_url)
                dependencies.add(dependency_url)
    return per_domain_ordering, dependencies

def get_ordering_from_response_file(response_filename, dependencies):
    per_domain_ordering = defaultdict(list)
    with open(response_filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            url = line[0]
            ts = int(line[2])
            if url in dependencies:
                parsed_url = urlparse(url)
                per_domain_ordering[parsed_url.netloc].append((url, ts))
    return per_domain_ordering

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('extended_waterfall_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--website', default=None)
    args = parser.parse_args()
    main(args.extended_waterfall_dir, args.dependency_dir)
