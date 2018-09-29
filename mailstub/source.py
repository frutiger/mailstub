# mailstub.source

import collections
import json
import re
import sys

import mailstub.util

def parse_labels(labels):
    label      = ''
    end_char   = ' '
    skip_next  = False
    for c in labels:
        if skip_next:
            skip_next = False
            continue
        if c == end_char:
            assert(label != '')
            yield label
            label    = ''
            end_char = ' '
            if c == '"':
                skip_next = True
        elif c == '"':
            end_char = '"'
        else:
            label += c
    yield label

def valid_label(label):
    return len(label) and label[0] != '"' and label[0] != '\\'

def flags(args):
    pattern = re.compile('\d+ \(UID (\d+) FLAGS \((.*)\)\)')

    result = collections.defaultdict(set)
    for data in mailstub.util.read(args, '(UID FLAGS)'):
        matches = pattern.match(data)
        uid, flags = matches.groups()
        result[int(uid)].update(flags.split())
    return result

def gm_labels(args):
    pattern = re.compile('\d+ \(X-GM-LABELS \((.*)\) UID (\d+)\)')

    result = collections.defaultdict(set)
    for data in mailstub.util.read(args, '(X-GM-LABELS UID)'):
        matches = pattern.match(data)
        labels, uid = matches.groups()
        result[int(uid)].update(filter(valid_label, parse_labels(labels)))
    return result

def main():
    mode = sys.argv.pop(1)
    args = mailstub.util.parse_mailbox_args('source')

    result = globals()[mode](args)

    output = { uid: list(values) for uid, values in result.items() }
    json.dump(list(output.items()), sys.stdout)

if __name__ == '__main__':
    main()

