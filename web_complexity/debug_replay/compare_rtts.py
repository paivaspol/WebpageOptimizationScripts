from argparse import ArgumentParser

DIFF_THRESHOLD = 25
PERCENT_DIFF_THRESHOLD = 0.1

def Main():
    first_mapping = GetMapping(args.first)
    second_mapping = GetMapping(args.second)
    increased = []
    decreased = []
    high_var = 0
    total = 0
    for k, v in first_mapping.items():
        if k not in second_mapping:
            continue
        total += 1
        second_v = second_mapping[k]
        diff = v - second_v
        percent_diff = 1.0 * diff / v
        if abs(percent_diff) > PERCENT_DIFF_THRESHOLD and \
            abs(diff) > DIFF_THRESHOLD:
            high_var += 1
            if diff < 0:
                # The value increased from the first snapshot.
                increased.append(diff)
            else:
                decreased.append(diff)
        if args.output_average:
            avg = 1.0 * (v + second_v) / 2
            print('{0} {1}'.format(k, avg))
        else:
            print('{0} {1} {2} {3}'.format(k, v, second_v, diff))

    if args.print_info:
        print('High diff: {0}({1}) increased: {2}({3})'.format(1.0 * high_var / total, high_var, 1.0 * len(increased) / total, len(increased)))
        print('Increased: ' + str(increased))
        print('Decreased: ' + str(decreased))


def GetMapping(filename):
    retval = dict()
    with open(filename, 'r') as input_file:
        for l in input_file:
            l = l.strip().split(' ')
            retval[l[0]] = float(l[1])
    return retval

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('first')
    parser.add_argument('second')
    parser.add_argument('--print-info', default=False, action='store_true')
    parser.add_argument('--output-average', default=False, action='store_true')
    args = parser.parse_args()
    Main()
