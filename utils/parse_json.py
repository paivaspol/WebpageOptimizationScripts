from argparse import ArgumentParser

import os
import simplejson as json

def main(root_dir, output_dir):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    pages = os.listdir(root_dir)
    for page in pages:
        tracing_filename = os.path.join(root_dir, page, 'tracing_' + page)
        output_filename = os.path.join(output_dir, page)
        
        with open(tracing_filename, 'rb') as input_file, \
             open(output_filename, 'wb') as output_file:
            output_file.write('[')
            just_started = True
            for raw_line in input_file:
                tracing_event = json.loads(json.loads(raw_line.strip()))
                if 'value' in tracing_event['params']:
                    for i in range(len(tracing_event['params']['value'])):
                        tracing_event_value = tracing_event['params']['value'][i]
                        if just_started:
                            just_started = False
                            output_file.write(json.dumps(tracing_event_value))
                        else:
                            output_file.write(',\n' + json.dumps(tracing_event_value))
            output_file.write(']')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('root_dir')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    main(args.root_dir, args.output_dir)
