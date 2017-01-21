from argparse import ArgumentParser

import os
import subprocess

def main(hostnames_dir):
    files = os.listdir(hostnames_dir)
    for f in files:
        full_path = os.path.join(hostnames_dir, f)
        org_info_dict = get_org_info_dict(full_path)
        print org_info_dict

def get_org_info_dict(page_filename):
    result = dict()
    with open(page_filename, 'rb') as input_file:
        for hostname in input_file:
            org = issue_whois(remove_www(hostname.strip()))
            if org is not None:
                result[hostname.strip()] = org
    return result

def issue_whois(domain):
    cmd = 'whois {0}'.format(domain)
    print cmd
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    print stdout
    for line in stdout:
        if 'Registrant Organization' in line:
            org = line.strip().split(': ')[1]
            return org
    return None

def remove_www(hostname):
    retval = hostname
    if retval.startswith('www.'):
        retval = retval[len('www.'):]
    return retval

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('hostnames_dir')
    args = parser.parse_args()
    main(args.hostnames_dir)
