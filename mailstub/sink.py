# mailstub.sink

import argparse
import collections
import imaplib
import json
import sys
from typing import cast, Callable, Dict, Iterator, List, Sequence, Set

import mailstub.util

State = Dict[int, Set[str]]

def collapse_ranges(numbers: Sequence[int]) -> str:
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

def invert_uid_to_strings(uid_to_string: State) -> Dict[str, Sequence[int]]:
    string_to_uids: Dict[str, List[int]] = collections.defaultdict(list)
    for uid, values in uid_to_string.items():
        for value in values:
            string_to_uids[value].append(uid)
    return cast(Dict[str, Sequence[int]], string_to_uids)

Func = Callable[[imaplib.IMAP4_SSL, State, argparse.Namespace], None]
Func2 = Callable[[State, Sequence[str]], None]

def with_session(func: Func) -> Func2:
    def wrapped(state: State, argv: Sequence[str]) -> None:
        args = mailstub.util.parse_mailbox_args('sink', argv)

        with mailstub.util.open_mailbox(args, 'sink') as session:
            assert(isinstance(session, imaplib.IMAP4_SSL))
            func(session, state, args)
    return wrapped

def store(session: imaplib.IMAP4_SSL, state: State, args: argparse.Namespace, operation: str) -> None:
    for flag, uids in invert_uid_to_strings(state).items():
        uid_ranges = collapse_ranges(uids)
        print('UID STORE {} {} {}'.format(uid_ranges, operation, flag))
        if not args.no_action:
            session.uid('STORE', uid_ranges, operation, flag)

@with_session
def flags(session: imaplib.IMAP4_SSL, state: State, args: argparse.Namespace) -> None:
    if args.args[0] == 'append':
        operation = '+FLAGS.SILENT'
    elif args.args[0] == 'remove':
        operation = '-FLAGS.SILENT'
    else:
        raise RuntimeError('Unknown sink operation')

    store(session, state, args, operation)

@with_session
def gm_labels(session: imaplib.IMAP4_SSL, state: State, args: argparse.Namespace) -> None:
    if args.args[0] == 'append':
        operation = '+X-GM-LABELS.SILENT'
    elif args.args[0] == 'remove':
        operation = '-X-GM-LABELS.SILENT'
    else:
        raise RuntimeError('Unknown sink operation')

    store(session, state, args, operation)

def uids(state: State, argv: Sequence[str]) -> None:
    for uid in state:
        print(uid)

def values(state: State, argv: Sequence[str]) -> None:
    result = set()
    for values in state.values():
        for value in values:
            result.add(value)
    for value in result:
        print(value)

def items(state: State, argv: Sequence[str]) -> None:
    for uid, values in state.items():
        print('{}: {}'.format(uid, ', '.join(values)))

def dump(state: State, argv: Sequence[str]) -> None:
    dumpable = {k: list(v) for k, v in state.items()}
    json.dump(dumpable, sys.stdout, indent=4, separators=(',', ': '))

def dispatch(state: State, argv: Sequence[str]) -> None:
    mode = argv[0]

    dispatcher = {
        'items':     items,
        'values':    values,
        'uids':      uids,
        'dump':      dump,
        'gm_labels': gm_labels,
        'flags':     flags,
    }

    if mode not in dispatcher:
        raise RuntimeError(f'Unknown sink: {mode}')

    dispatcher[mode](state, argv[1:])

