from argparse import ArgumentParser

def main(raw_data_filename, filetype):
    with open(raw_data_filename, 'rb') as input_file:
        cur_page = None
        for raw_line in input_file:
            line = raw_line.strip()
            if not raw_line.startswith('\t'):
                cur_page = line
            else:
                if line.startswith(filetype):
                    splitted_line = line.split()
                    print cur_page + ' ' + splitted_line[1] + ' ' + splitted_line[2]

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('raw_data_file')
    parser.add_argument('filetype')
    args = parser.parse_args()
    main(args.raw_data_file, args.filetype)
