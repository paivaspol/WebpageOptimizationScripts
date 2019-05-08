from argparse import ArgumentParser

def main(filename):
    with open(filename, 'rb') as input_file:
        for raw_line in input_file:
            line = raw_line.strip().split()
            if len(line) > 3:
                url = line[0]
                recv_and_send_req = int(line[2]) - int(line[1])
                send_req_and_recv_res = int(line[3]) - int(line[2])
                print url + ' ' + str(recv_and_send_req) + ' ' + str(send_req_and_recv_res)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('filename')
    args = parser.parse_args()
    main(args.filename)
