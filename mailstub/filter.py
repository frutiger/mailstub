# mailstub.filter

import json
import re
import sys

def load_mapping(mapping_file):
    mapping = {}
    for line in mapping_file:
        try:
            items = line.split()
            mapping[int(items[0])] = int(items[1])
        except:
            pass
    return mapping

def map_uids(args, data):
    with open(args[1]) as f:
        mapping = load_mapping(f)
    result = {}
    for uid, values in data.items():
        result[mapping[uid]] = values
    return result

def add(args, data):
    for values in data.values():
        values.add(args[1])
    return data

def remove(args, data):
    for values in data.values():
        values.remove(args[1])
    return data

def replace_all(args, data):
    result = {}
    for uid, values in data.items():
        replacement = set()
        for value in values:
            replacement.add(value.replace(args[1], args[2]))
        result[uid] = replacement
    return result

def pattern_any(args, data):
    regex = re.compile(args[1])
    result = {}
    for uid, values in data.items():
        if any([regex.match(value) for value in values]):
            result[uid] = values
    return result

def pattern_all(args, data):
    regex = re.compile(args[1])
    result = {}
    for uid, values in data.items():
        if all([regex.match(value) for value in values]):
            result[uid] = values
    return result

def pattern(args, data):
    regex = re.compile(args[1])
    result = {}
    for uid, values in data.items():
        result[uid] = set([value for value in values if regex.match(value)])
    return result

def main():
    data = { uid: set(values) for uid, values in json.load(sys.stdin) }

    mode = sys.argv.pop(1)
    result = globals()[mode](sys.argv, data)

    output = { uid: list(values) for uid, values in result.items() }
    json.dump(list(output.items()), sys.stdout)

if __name__ == '__main__':
    main()

