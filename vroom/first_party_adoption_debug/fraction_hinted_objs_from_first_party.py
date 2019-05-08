from argparse import ArgumentParser
from collections import defaultdict
from urlparse import urlparse

import common_module
import json
import os

def main(domains, root_dir, dependencies, dependency_parents):
    for p in os.listdir(root_dir):
        if args.debug is not None and args.debug not in p:
            continue
        network_filename = os.path.join(root_dir, p, 'network_' + p)
        page_domains = domains[p]
        page_dependencies = dependencies[p]
        urls_to_parents = dependency_parents[p]
        urls = get_urls(network_filename, p, page_dependencies)
        first_party_count = 0
        counted_urls = []
        for url in urls:
            if url in urls_to_parents:
                domain = urlparse(url).netloc
                parent_domain = urlparse(urls_to_parents[url]).netloc
                if parent_domain in page_domains:
                    counted_urls.append(url)
                    first_party_count += 1
        if len(urls) > 0:
            fraction = 1.0 * first_party_count / len(urls)
            print '{0} {1} {2} {3}'.format(p, first_party_count, len(urls), fraction)
        if args.debug:
            print urls
            print ''
            print page_domains
            print ''
            print counted_urls

def get_urls(network_filename, p, dependencies):
    urls = []
    with open(network_filename, 'rb') as input_file:
        found_first_request = False
        for l in input_file:
            network_event = json.loads(l.strip())
            if network_event['method'] == 'Network.requestWillBeSent':
                url = network_event['params']['request']['url']
                if not found_first_request:
                    if common_module.escape_page(url) == p:
                        found_first_request = True
                
            elif found_first_request and network_event['method'] == 'Network.responseReceived':
                url = network_event['params']['response']['url']
                if not url.startswith('data:') and url in dependencies and url not in urls:
                    urls.append(url)
    return urls

def get_domains(domains_dir):
    result = defaultdict(set)
    for p in os.listdir(domains_dir):
        input_filename = os.path.join(domains_dir, p)
        with open(input_filename, 'rb') as input_file:
            for d in input_file:
                result[p].add(d.strip())
    return result

def get_dependencies(dependency_dir):
    result = defaultdict(set)
    dependency_parents = defaultdict(set)
    for p in os.listdir(dependency_dir):
        input_filename = os.path.join(dependency_dir, p, 'dependency_tree.txt')
        if not os.path.exists(input_filename):
            continue
        with open(input_filename, 'rb') as input_file:
            url_to_parent_map = dict()
            for d in input_file:
                splitted_line = d.strip().split()
                result[p].add(splitted_line[2])
                url_to_parent_map[splitted_line[2]] = splitted_line[0]
            dependency_parents[p] = url_to_parent_map
    return result, dependency_parents

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('domains_dir')
    parser.add_argument('dependency_dir')
    parser.add_argument('--debug')
    args = parser.parse_args()
    domains = get_domains(args.domains_dir)
    dependencies, dependency_parents = get_dependencies(args.dependency_dir)
    main(domains, args.root_dir, dependencies, dependency_parents)
