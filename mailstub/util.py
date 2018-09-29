# mailstub.util

import argparse
import contextlib
import imaplib
import os

def parse_mbsyncrc(path='~/.mbsyncrc'):
    accounts = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            if not line.startswith('IMAPAccount'):
                continue

            name = line.split()[1]
            for line in f:
                if line.startswith('Host'):
                    host = line.split()[1]
                if line.startswith('User'):
                    user = line.split()[1]
                if line.startswith('Pass'):
                    pw = line.split()[1]
                if line == '\n':
                    accounts[name] = {
                        'host': host,
                        'user': user,
                        'pass': pw,
                    }
                    break
    return accounts

def parse_mailbox_args(flow):
    parser = argparse.ArgumentParser()
    parser.add_argument('account')
    parser.add_argument('mailbox')
    if flow == 'source':
        parser.add_argument('-m', '--max_messages', type=int)
    elif flow == 'sink':
        parser.add_argument('-n', '--no_action', action='store_true')
    parser.add_argument('args', nargs='*')
    return parser.parse_args()

@contextlib.contextmanager
def open_mailbox(args, flow):
    account = parse_mbsyncrc()[args.account]
    session = imaplib.IMAP4_SSL(account['host'])
    session.login(account['user'], account['pass'])

    if flow == 'source':
        response = session.select(mailbox=args.mailbox, readonly=True)
        num_msgs = int(response[1][0].decode('ascii'))
        if args.max_messages is not None:
            num_msgs = min(num_msgs, args.max_messages)
        yield session, num_msgs
    elif flow == 'sink':
        session.select(mailbox=args.mailbox, readonly=False)
        yield session
    else:
        raise RuntimeError('Unsupported flow: ' + flow)

    session.close()
    session.logout()

def read(args, names):
    with open_mailbox(args, 'source') as (session, num_msgs):
        for item in session.fetch('1:{}'.format(num_msgs), names)[1]:
            yield item.decode('ascii')

