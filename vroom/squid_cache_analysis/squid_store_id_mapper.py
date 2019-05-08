#!/usr/bin/env python -u

import re
import sys

RULES_FILENAME = 'rules.txt.bak'

def read_rules(filename):
    rules = []
    with open(filename, 'rb') as input_file:
        for line in input_file:
            rules.append(line.strip().split())
    return rules

def construct_regexs(rules):
    results = dict()
    for rule, replacement in rules:
        results[re.compile(rule)] = replacement
    return results

# Construct the necessary rules and patterns
rules = read_rules(RULES_FILENAME)
patterns = construct_regexs(rules)

while True:
    line = sys.stdin.readline().strip()
    if not line or line == '' or line == 'quit':
        break
    try:
        splitted = line.split()
        channel_id = None
        if len(splitted) == 1:
            # Contains only the URL
            url = line.strip()
        elif len(splitted) == 2 and splitted[0].isdigit():
            channel_id = int(splitted[0])
            url = splitted[1]
        else:
            continue

        matched = False
        retval = 'ERR'
        for pattern in patterns:
            if pattern.match(url) is not None:
                replacement_url = patterns[pattern]
                retval = 'OK store-id={0}'.format(replacement_url)
                break
        if channel_id is not None:
            retval = str(channel_id) + ' ' + retval    
        print retval

    except Exception as e:
        raise e

sys.stdout.flush()
