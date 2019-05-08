from argparse import ArgumentParser

import os

NO_MATCH = '[NO_MATCH]'

def Main():
    for d in os.listdir(args.root_dir):
        filename = os.path.join(args.root_dir, d)
        retval = AnalyzeFile(filename)
        print('{0} {1}'.format(d, ' '.join(retval)))


def AnalyzeFile(filename):
    '''Returns a list containing the values below.'''
    mahimahi_match = 0
    sift4_match = 0
    mahimahi_match_but_404 = 0
    mahimahi_no_match_but_sift4_match = 0
    mahimahi_match_but_no_sift4_match = 0
    count_404 = 0
    all_urls = 0
    with open(filename, 'r') as input_file:
        for l in input_file:
            all_urls += 1
            l = l.strip().split()
            status_code = int(l[len(l) - 1])
            mahimahi_url = l[1]
            sift4_url = l[2]

            if status_code == 404 and mahimahi_url != NO_MATCH:
                mahimahi_match_but_404 += 1
            if mahimahi_url == NO_MATCH and sift4_url != NO_MATCH:
                mahimahi_no_match_but_sift4_match += 1
            if mahimahi_url != NO_MATCH and sift4_url == NO_MATCH:
                mahimahi_match_but_no_sift4_match += 1
            if mahimahi_match != NO_MATCH:
                mahimahi_match += 1
            if sift4_url != NO_MATCH:
                sift4_match += 1
            if status_code == 404:
                count_404 += 1

    return [ str(mahimahi_match),
             str(sift4_match),
             str(mahimahi_match_but_404),
             str(mahimahi_match_but_no_sift4_match),
             str(mahimahi_no_match_but_sift4_match),
             str(count_404),
             str(all_urls) ]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    args = parser.parse_args()
    Main()
