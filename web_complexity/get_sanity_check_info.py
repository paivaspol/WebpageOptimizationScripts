'''
This script takes a directory of an experiment and produces a file
that contains the information to perform sanity check on the HTTPArchive dataset.
'''
from argparse import ArgumentParser

import json
import os

class PageInfo:
    '''
    Holds the info for a page.
    '''
    def AddRequest(self, url):
        '''
        Adds a request to this page info.
        '''
        if url.startswith('data'):
            return
        self.requests.add(url)


    def AddTotalEncodedBytes(self, num_bytes):
        '''
        Adds the number of bytes into the total bytes.
        '''
        self.total_encoded_bytes_ += max(0, num_bytes)


    def AddTotalBytes(self, num_bytes):
        '''
        Adds the number of bytes into the total non-encoded bytes.
        '''
        self.total_bytes_ += max(0, num_bytes)


    def __str__(self):
        '''
        Returns the string representation of this PageInfo object.
        '''
        # retval = '{0} {1} {2}'.format( \
        #         len(self.requests), \
        #         self.total_bytes_, \
        #         self.total_encoded_bytes_)
        retval = args.delim.join(
                [ str(len(self.requests)), \
                str(self.total_bytes_), \
                str(self.total_encoded_bytes_) ])
        return retval


    def __init__(self):
        self.requests = set()
        self.total_bytes_ = 0
        self.total_encoded_bytes_ = 0


def GetInfo(network_filename):
    '''
    GetInfo returns a PageInfo object with the fields populated.
    '''
    with open(network_filename, 'r') as input_file:
        page_info = PageInfo()
        for l in input_file:
            e = json.loads(l.strip())
            if e['method'] == 'Network.requestWillBeSent':
                url = e['params']['request']['url']
                page_info.AddRequest(url)
            elif e['method'] == 'Network.dataReceived':
                page_info.AddTotalBytes(e['params']['dataLength'])
                page_info.AddTotalEncodedBytes(e['params']['encodedDataLength'])
        return page_info


def main():
    for p in os.listdir(args.root_dir):
        network_filename = os.path.join(args.root_dir, p, 'network_' + p)
        if not os.path.exists(network_filename):
            continue
        info = GetInfo(network_filename)
        print args.delim.join([ \
            'http://www.' + p + '/', \
            str(info) ])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--delim', default=' ')
    args = parser.parse_args()
    main()
