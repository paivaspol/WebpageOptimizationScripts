import common_module
import requests 
import os
import subprocess

from time import sleep

WHOIS_CMD = 'whois {0}'
DATABASE_DIR = 'whois_database'
RAW_FILE_DIR = 'raw_file'
WHOIS_MAP = 'whois_org_dict.txt'
WAIT = 1.0

class WhoIsDictionary:
    '''
    A class for fetching WhoIs.
    '''
    def __init__(self):
        self.whois_org_dict = self.populate_dictionary_from_disk()
        common_module.create_directory_if_not_exists(DATABASE_DIR)
        raw_file_dir = os.path.join(DATABASE_DIR, RAW_FILE_DIR)
        common_module.create_directory_if_not_exists(raw_file_dir)

    def get_registrant_for_domain(self, domain):
        if domain not in self.whois_org_dict:
            # Fetch from network.
            self.fetch_whois_record_from_network(domain)
        sleep(WAIT)
        return self.whois_org_dict[domain]
    
    def domain_exists(self, domain):
        return domain in self.whois_org_dict

    def fetch_whois_record_from_network(self, domain):
        process = subprocess.Popen(WHOIS_CMD.format(domain), \
                                   shell=True, stdout=subprocess.PIPE, \
                                   stderr=subprocess.PIPE)
        response_text, err = process.communicate()
        if len(err) != 0:
            print '{0} {1}'.format(domain, err)
        self.write_whois_record_to_file(domain, response_text)
        registrant_org = self.extract_registrant_org(response_text)
        self.whois_org_dict[domain] = registrant_org
        self.write_domain_to_org_to_file(domain, registrant_org)

    def write_whois_record_to_file(self, domain, response_text):
        full_path = os.path.join(DATABASE_DIR, RAW_FILE_DIR, domain)
        with open(full_path, 'wb') as output_file:
            output_file.write(response_text)

    def extract_registrant_org(self, response_text):
        tokenized_response = response_text.strip().split('\n')
        for response_line in tokenized_response:
            line = response_line.strip()
            if line.startswith('Registrant Organization:'):
                return line[len('Registrant Organization: '):]
        return None

    def write_domain_to_org_to_file(self, domain, org):
        whois_map_path = os.path.join(DATABASE_DIR, WHOIS_MAP)
        with open(whois_map_path, 'ab') as output_file:
            output_file.write('{0} {1}\n'.format(domain, org))
    
    def populate_dictionary_from_disk(self):
        result = dict()
        whois_map_path = os.path.join(DATABASE_DIR, WHOIS_MAP)
        if os.path.exists(whois_map_path):
            with open(whois_map_path, 'rb') as input_file:
                for raw_line in input_file:
                    line = raw_line.strip().split()
                    result[line[0]] = line[1]
        return result
