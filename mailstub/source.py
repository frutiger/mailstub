# mailstub.source

import argparse
import collections
import json
import re
import sys
from typing import Dict, Iterator, Sequence, Set

import mailstub.util

State = Dict[int, Set[str]]

def parse_labels(labels: Sequence[str]) -> Iterator[str]:
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

def valid_label(label: str) -> bool:
    if len(label) and label[0] != '"' and label[0] != '\\':
        return True
    else:
        return False

def flags(args: argparse.Namespace) -> State:
    pattern = re.compile('\d+ \(UID (\d+) FLAGS \((.*)\)\)')

    result: State = collections.defaultdict(set)
    for data in mailstub.util.read(args, '(UID FLAGS)'):
        matches = pattern.match(data)
        if matches is None:
            raise RuntimeError(f'Failed to parse: {data}')
        uid, flags = matches.groups()
        result[int(uid)].update(flags.split())
    return result

def gm_labels(args: argparse.Namespace) -> State:
    pattern = re.compile('\d+ \(X-GM-LABELS \((.*)\) UID (\d+)\)')

    result: State = collections.defaultdict(set)
    for data in mailstub.util.read(args, '(X-GM-LABELS UID)'):
        matches = pattern.match(data)
        if matches is None:
            raise RuntimeError(f'Failed to parse: {data}')
        labels, uid = matches.groups()
        result[int(uid)].update(filter(valid_label, parse_labels(labels)))
    return result

def dispatch(argv: Sequence[str]) -> State:
    mode = argv[0]
    args = mailstub.util.parse_mailbox_args('source', argv[1:])

    dispatcher = {
        'flags':     flags,
        'gm_labels': gm_labels,
    }

    if mode not in dispatcher:
        raise RuntimeError(f'Unknown source: {mode}')

    return dispatcher[mode](args)

