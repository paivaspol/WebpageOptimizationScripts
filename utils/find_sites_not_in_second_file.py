from argparse import ArgumentParser

def parse_file(filename):
    result = set()
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            result.add(line[0])
    return result

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first_file')
    parser.add_argument('second_file')
    args = parser.parse_args()
    first_file = parse_file(args.first_file)
    second_file = parse_file(args.second_file)
    results = first_file - second_file
    for result in results:
        print result

