# mailstub.sink

import collections
import json
import sys

import mailstub.util

def collapse_ranges(numbers):
    ranges     = []
    start, end = None, None
    for n in sorted(numbers):
        if start is None:
            start, end = n, n
            continue
        if n == end + 1:
            end = n
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append('{}:{}'.format(start, end))
            start, end = n, n
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append('{}:{}'.format(start, end))
    return ','.join(ranges)

def invert_uid_to_strings(uid_to_string):
    string_to_uids = collections.defaultdict(list)
    for uid, values in uid_to_string.items():
        for value in values:
            string_to_uids[value].append(uid)
    return string_to_uids

def with_session(func):
    def wrapped(data):
        args = mailstub.util.parse_mailbox_args('sink')

        with mailstub.util.open_mailbox(args, 'sink') as session:
            return func(session, args, data)
    return wrapped

def store(session, args, data, operation):
    for flag, uids in invert_uid_to_strings(data).items():
        uid_ranges = collapse_ranges(uids)
        print('UID STORE {} {} {}'.format(uid_ranges, operation, flag))
        if not args.no_action:
            session.uid('STORE', uid_ranges, operation, flag)

@with_session
def flags(session, args, data):
    if args.args[0] == 'append':
        operation = '+FLAGS.SILENT'
    elif args.args[0] == 'remove':
        operation = '-FLAGS.SILENT'
    else:
        raise RuntimeError('Unknown sink operation')

    store(session, args, data, operation)

@with_session
def gm_labels(session, args, data):
    if args.args[0] == 'append':
        operation = '+X-GM-LABELS.SILENT'
    elif args.args[0] == 'remove':
        operation = '-X-GM-LABELS.SILENT'
    else:
        raise RuntimeError('Unknown sink operation')

    store(session, args, data, operation)

def print_uids(data):
    for uid in data:
        print(uid)

def print_values(data):
    result = set()
    for values in data.values():
        for value in values:
            result.add(value)
    for value in result:
        print(value)

def print_items(data):
    for uid, values in data.items():
        print('{}: {}'.format(uid, ', '.join(values)))

def main():
    data = { uid: set(values) for uid, values in json.load(sys.stdin) }
    mode = sys.argv.pop(1)

    globals()[mode](data)

if __name__ == '__main__':
    main()

