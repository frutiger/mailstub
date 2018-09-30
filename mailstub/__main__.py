# mailstub

import sys
from typing import Dict, Sequence, TextIO

import mailstub.filter
import mailstub.sink
import mailstub.source

class InvalidCommandError(Exception):
    pass

def main(argv:   Sequence[str] = sys.argv,
         stdin:  TextIO        = sys.stdin,
         stdout: TextIO        = sys.stdout,
         stderr: TextIO        = sys.stderr) -> int:
    if len(argv) >= 2 and argv[1] != '-':
        stdin = open(argv[1])

    commands = []
    first_run = True
    for line in stdin:
        tokens = ['']
        escaped = False
        for c in line[:-1]:
            if escaped:
                escaped = False
                tokens[-1] += c
            else:
                if c == '\\':
                    escaped = True
                elif c == ' ':
                    tokens.append('')
                else:
                    tokens[-1] += c

        if tokens[0][0] == '#':
            continue

        if first_run:
            first_run = False
            if tokens[0] != 'source':
                print('Program did not begin with a source', file=stderr)
                return 1

        commands.append(tokens)

    if commands[-1][0] != 'sink':
        print('Program did not end with a sink', file=stderr)
        return 1

    for tokens in commands:
        if tokens[0] == 'source':
            state = mailstub.source.dispatch(tokens[1:])
        if tokens[0] == 'filter':
            state = mailstub.filter.dispatch(state, tokens[1:])
        elif tokens[0] == 'sink':
            mailstub.sink.dispatch(state, tokens[1:])

    return 0

if __name__ == '__main__':
    sys.exit(main())

