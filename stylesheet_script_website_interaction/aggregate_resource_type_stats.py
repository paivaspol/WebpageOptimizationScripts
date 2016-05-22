from argparse import ArgumentParser

def parse_stat_file(stat_filename, resource_type):
    result = dict()
    with open(stat_filename, 'rb') as input_file:
        cur_page = None
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) == 1:
                cur_page = line[0]
            elif raw_line.startswith('\t') and resource_type in line[0]:
                if 'other' in resource_type:
                    print '{0} {1} {2} {3}'.format(cur_page, line[2], line[3], line[4])
                else:
                    print '{0} {1} {2} {3}'.format(cur_page, line[1], line[2], line[3])


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('stat_filename')
    parser.add_argument('resource_type')
    args = parser.parse_args()
    parse_stat_file(args.stat_filename, args.resource_type)
