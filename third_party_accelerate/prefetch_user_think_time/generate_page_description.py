import sys
import json

page_list_filename = sys.argv[1]

with open(page_list_filename, 'r') as input_file:
    final_obj = []
    output_obj = {}
    for l in input_file:
        l = l.strip()
        if len(l) == 0:
            final_obj.append(output_obj)
            output_obj = {}
        elif l.startswith('#'):
            output_obj['type'] = l[2:]
            output_obj['urls'] = []
        else:
            output_obj['urls'].append(l)
    final_obj.append(output_obj)
    print json.dumps(final_obj)
