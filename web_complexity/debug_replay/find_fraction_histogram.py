from argparse import ArgumentParser
from collections import defaultdict

import os

def Main():
    types = set()
    type_count = defaultdict(lambda: defaultdict(int))
    type_bytes = defaultdict(lambda: defaultdict(int))
    page_missing_total_count = defaultdict(int)
    page_missing_total_bytes = defaultdict(int)
    total_count = 0
    total_bytes = 0
    for d in os.listdir(args.root_dir):
        filename = os.path.join(args.root_dir, d, 'missing')
        with open(filename, 'r') as input_file:
            for l in input_file:
                if not l.startswith('http'):
                    continue
                l = l.strip().split()
                size = int(l[1])
                res_type = l[2]
                if res_type not in types:
                    types.add(res_type)
                type_bytes[d][res_type] += size
                type_count[d][res_type] += 1
                page_missing_total_count[d] += 1
                page_missing_total_bytes[d] += size
                total_bytes += size
                total_count += 1
                if args.print_missing_type is None or args.print_missing_type == res_type:
                    print('{0}\t{1}'.format(d, l[0]))

    pages_order_bytes = defaultdict(list)
    pages_order_count = defaultdict(list)

    for p in type_count:
        for t in type_count[p]:
            try:
                bytes_frac = 1.0 * type_bytes[p][t] / page_missing_total_bytes[p]
                pages_order_bytes[t].append((p, bytes_frac))
                count_frac = 1.0 * type_count[p][t] / page_missing_total_count[p]
                pages_order_bytes[t].append((p, count_frac))
            except Exception as e:
                pass

    for t in types:
        sum_type_counts = sum_dict(type_count, t)
        sum_type_bytes = sum_dict(type_bytes, t)
        print('{0} {1} {2}'.format(t, sum_type_counts, 1.0 * sum_type_counts / total_count))
        print('{0} {1} {2}'.format(t, sum_type_bytes, 1.0 * sum_type_bytes / total_bytes))
        print()

    # for t in types:
    #     print('{0}: {1}'.format(t, GetTopFive(pages_order_bytes[t])))


def GetTopFive(list_to_get):
    return sorted(list_to_get, key=lambda x: x[1], reverse=True)[0:5]


def sum_dict(dict_val, t):
    final_sum = 0
    for p in dict_val:
        for pt in dict_val[p]:
            if pt != t:
                continue
            final_sum += dict_val[p][pt]
    return final_sum


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('--output-page', choices=[ 'bytes', 'count' ])
    parser.add_argument('--print-missing-type', choices=[ 'image', 'script' ], default=None)
    args = parser.parse_args()
    Main()
