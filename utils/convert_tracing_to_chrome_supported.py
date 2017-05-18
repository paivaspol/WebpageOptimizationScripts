from argparse import ArgumentParser

import os
import json

def main(tracing_filename, output_filename):
    with open(tracing_filename, 'rb') as input_file, \
         open(output_filename, 'wb') as output_file:
        output_file.write('[')
        just_started = True
        event = ''
        cur_line = input_file.readline()
        while cur_line != '':
            if 'Tracing.dataCollected' in cur_line and \
                event != '':
                # process the current event.
                try:
                    tracing_event = json.loads(event)
                except Exception:
                    event = ''
                    continue
                if 'value' in tracing_event['params']:
                    for i in range(len(tracing_event['params']['value'])):
                        tracing_event_value = tracing_event['params']['value'][i]
                        if just_started:
                            just_started = False
                            output_file.write(json.dumps(tracing_event_value))
                        else:
                            output_file.write(',\n' + json.dumps(tracing_event_value))
                event = ''
            event += cur_line.strip()
            cur_line = input_file.readline()
        output_file.write(']')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('tracing_filename')
    parser.add_argument('output_filename')
    args = parser.parse_args()
    main(args.tracing_filename, args.output_filename)
