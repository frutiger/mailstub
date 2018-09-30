# mailstub.filter

import json
import re
import sys
from typing import Dict, List, Sequence, Set, TextIO

State = Dict[int, Set[str]]

def load_mapping(mapping_file: TextIO) -> Dict[int, int]:
    mapping = {}
    for line in mapping_file:
        try:
            items = line.split()
            mapping[int(items[0])] = int(items[1])
        except:
            pass
    return mapping

def map_uids(data: State, args: Sequence[str]) -> State:
    with open(args[0]) as f:
        mapping = load_mapping(f)
    result = {}
    for uid, values in data.items():
        result[mapping[uid]] = values
    return result

def add(data: State, args: Sequence[str]) -> State:
    for values in data.values():
        values.add(args[0])
    return data

def remove(data: State, args: Sequence[str]) -> State:
    for values in data.values():
        if args[0] in values:
            values.remove(args[0])
    return data

def remove_all(data: State, args: Sequence[str]) -> State:
    return {uid: set() for uid in data}

def replace_all(data: State, args: Sequence[str]) -> State:
    result = {}
    for uid, values in data.items():
        replacement = set()
        for value in values:
            replacement.add(value.replace(args[0], args[1]))
        result[uid] = replacement
    return result

def pattern_message_any(data: State, args: Sequence[str]) -> State:
    regex = re.compile(args[0])
    result = {}
    for uid, values in data.items():
        if any([regex.match(value) for value in values]):
            result[uid] = values
    return result

def pattern_message_all(data: State, args: Sequence[str]) -> State:
    regex = re.compile(args[0])
    result = {}
    for uid, values in data.items():
        if all([regex.match(value) for value in values]):
            result[uid] = values
    return result

def pattern(data: State, args: Sequence[str]) -> State:
    regex = re.compile(args[0])
    result = {}
    for uid, values in data.items():
        result[uid] = set([value for value in values if regex.match(value)])
    return result

def pattern_invert(data: State, args: Sequence[str]) -> State:
    regex = re.compile(args[0])
    result = {}
    for uid, values in data.items():
        result[uid] = set([value for value in values if not regex.match(value)])
    return result

def split(data: State, args: Sequence[str]) -> State:
    result = {}
    for uid, values in data.items():
        new_values: List[str] = []
        for value in values:
            new_values += value.split(args[0])
        result[uid] = set(new_values)
    return result

def dispatch(state: State, argv: Sequence[str]) -> State:
    mode = argv[0]

    dispatcher = {
        'map_uids':            map_uids,
        'add':                 add,
        'remove':              remove,
        'remove_all':          remove_all,
        'replace_all':         replace_all,
        'pattern_message_any': pattern_message_any,
        'pattern_message_all': pattern_message_all,
        'pattern':             pattern,
        'pattern_invert':      pattern_invert,
        'split':               split,
    }

    if mode not in dispatcher:
        raise RuntimeError(f'Unknown filter: {mode}')

    return dispatcher[mode](state, argv[1:])

