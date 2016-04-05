from argparse import ArgumentParser

import collections
import os

HTTPS_PREFIX = 'https://'
HTTP_PREFIX = 'http://'
WWW_PREFIX = 'www.'

def main(root_dir):
    all_urls = get_all_urls_from_all_files(root_dir)
    urls_with_duplicates_removed = set(all_urls)
    all_domains = extract_domains(all_urls)
    unique_domains = set(all_domains)
    all_without_subdomains = extract_domains(all_domains, extract_subdomain=True)
    unique_without_subdomains = set(all_without_subdomains)
    counter = collections.Counter(all_domains)
    print_histogram(counter.most_common())
    counter_without_subdomains = collections.Counter(all_without_subdomains)
    print_histogram(counter_without_subdomains.most_common())
    print 'All URLs:\t' + str(len(all_urls))
    print 'Unique URLs:\t' + str(len(urls_with_duplicates_removed))
    print 'Unique Domains:\t' + str(len(unique_domains))
    print 'Unique Domains without subdomain:\t' + str(len(unique_without_subdomains))

def print_histogram(histogram):
    for key, count in histogram:
        print key + ' ' + str(count)

def get_all_urls_from_all_files(root_dir):
    result_urls = []
    for path, dirs, filenames in os.walk(root_dir):
        if len(filenames) == 0:
            continue
        for filename in filenames:
            full_path = os.path.join(path, filename)
            with open(full_path, 'rb') as input_file:
                for line in input_file:
                    result_urls.append(line)
    return result_urls

def extract_domains(url_list, extract_subdomain=False):
    domain_list = []
    for url in url_list:
        if not extract_subdomain:
            domain_list.append(extract_domain(url))
        elif extract_subdomain:
            domain_list.append(remove_subdomain(url))
    return domain_list

def extract_domain(url):
    url = url_remove_scheme_and_www(url)
    slash_index = url.index('/')
    domain = url[:slash_index]
    return domain

def remove_subdomain(domain):
    splitted_domain = domain.split('.')
    return splitted_domain[len(splitted_domain) - 2] + '.' + splitted_domain[len(splitted_domain) - 1]

def url_remove_scheme_and_www(url):
    if url.startswith(HTTPS_PREFIX):
        url = url[len(HTTPS_PREFIX):]
    elif url.startswith(HTTP_PREFIX):
        url = url[len(HTTP_PREFIX):]
    if url.startswith(WWW_PREFIX):
        url = url[len(WWW_PREFIX):]
    return url

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    main(args.root_dir)

