#!/usr/bin/env python

import io
import csv
import argparse
import subprocess
from drawbox import Box, PY2
from drawbox.csvless.getenv import Env

# TODO
# - [x] auto header
# - [ ] generated line number
# - [ ] wrap row


def main():
    """
    Render a CSV file in the console as a human readable table
    """
    parser = init_parser()

    args, reader_kwgs = parse_args(parser)

    f = open_file(args.file, encoding=args.encoding)
    reader = csv.reader(f, **reader_kwgs)

    box = Box(
        max_col_width=args.max_column_width,
        table_style=args.table_style,
        auto_header=args.auto_header,
    )

    if args.cat:
        box.draw(reader)
        f.close()
    else:
        less_cmd = ['less', '-S']
        if args.line_numbers:
            less_cmd.append('-N')

        p = subprocess.Popen(less_cmd, stdin=subprocess.PIPE)

        counts = {'w': 0}
        if PY2:
            def writer(line):
                p.stdin.write(line)
                counts['w'] += 1
        else:
            def writer(line):
                p.stdin.write(line.encode())
                counts['w'] += 1

        try:
            box.draw(reader, writer=writer)
        except BrokenPipeError as e:
            if counts['w'] == 0:
                print('Zero success write before BrokenPipeError')
                raise e

        f.close()
        p.communicate()


def init_parser():
    # env vars
    Env.set_prefix('CSVLESS')

    ENV_MAX_COL_WIDTH = Env('{prefix}_MAX_COLUMN_WIDTH', type=int, default=32)
    ENV_LINE_NUMBERS = Env('{prefix}_LINE_NUMBERS', type=bool, default=False)
    ENV_TABLE_STYLE = Env('{prefix}_TABLE_STYLE', type=str, default='base')

    env_help = 'Environment Variables:\n'
    env_key_max_len = max([len(i.key) for i in Env._instances.values()])
    env_key_tmpl = '  {:<' + str(env_key_max_len) + '}\t{}\n'
    for i in Env._instances.values():
        env_help += env_key_tmpl.format(i.key, 'default: {}'.format(i.default))
    env_help = env_help[:-1]

    # the `formatter_class` can make description & epilog show multiline
    parser = argparse.ArgumentParser(
        description='Render a CSV file in the console as a Markdown-compatible, fixed-width table.',
        epilog=env_help,
        usage='csvless [options] FILE',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # arguments
    parser.add_argument('file', metavar="FILE", type=str, help="csv file")

    # display options
    display_group = parser.add_argument_group('Display options')
    display_group.add_argument(
        '-w', '--max-column-width', dest='max_column_width', type=int,
        default=ENV_MAX_COL_WIDTH.get(),
        help='Truncate all columns to at most this width. The remainder will be replaced with ellipsis.')
    display_group.add_argument(
        '-N', '--line-numbers', dest='line_numbers', action='store_true',
        default=ENV_LINE_NUMBERS.get(),
        help='Show line numbers in the pager')
    display_group.add_argument(
        '-s', '--table-style', dest='table_style', type=str, choices=list(Box.table_styles.keys()),
        default=ENV_TABLE_STYLE.get(),
        help='Display style for the table, default is `base`')
    display_group.add_argument(
        '--cat', dest='cat', action='store_true',
        help='Behave like cat, print to stdout directly')
    display_group.add_argument(
        '-H', '--auto-header', dest='auto_header', action='store_true',
        help=('Specify that the input CSV file has no header row. '
              'Will create auto header (a,b,c,...).'))

    # file options
    file_group = parser.add_argument_group('File options')
    file_group.add_argument(
        '-e', '--encoding', dest='encoding', default='utf-8',
        help='Specify the encoding of the input CSV file.')

    # reader options
    reader_group = parser.add_argument_group('CSV reader options')
    reader_group.add_argument(
        '-d', '--delimiter', dest='delimiter',
        help='Delimiting character of the input CSV file.')
    reader_group.add_argument(
        '--no-doublequote', dest='doublequote', action='store_false',
        help='Whether or not double quotes are doubled in the input CSV file.')
    reader_group.add_argument(
        '--escapechar', dest='escapechar',
        help=('Character used to escape the delimiter if --quoting 3 ("Quote None") '
              'is specified and to escape the QUOTECHAR if --no-doublequote is specified.'))
    reader_group.add_argument(
        '--quotechar', dest='quotechar',
        help='Character used to quote strings in the input CSV file.')
    reader_group.add_argument(
        '--quoting', dest='quoting', type=int, choices=[0, 1, 2, 3],
        help=('Quoting style used in the input CSV file. 0 = Quote All, '
              '1 = Quote Minimal, 2 = Quote Non-numeric, 3 = Quote None.'))
    reader_group.add_argument(
        '--skipinitialspace', dest='skipinitialspace', action='store_true',
        help='Ignore whitespace immediately following the delimiter.')

    return parser


def parse_args(parser):
    args = parser.parse_args()

    # reader args
    reader_kwgs = get_reader_kwargs(args)
    return args, reader_kwgs


def get_reader_kwargs(args):
    """
    Extracts those from the command-line arguments those would should be passed through to the input CSV reader(s).
    """
    kwargs = {}

    if args.delimiter == '\\t':
        args.delimiter = '\t'

    for arg in ('delimiter', 'doublequote', 'escapechar', 'quotechar', 'skipinitialspace'):
        value = getattr(args, arg)
        if value is not None:
            kwargs[arg] = value

    if args.quoting:
        kwargs['quoting'] = {
            0: csv.QUOTE_ALL,
            1: csv.QUOTE_MINIMAL,
            2: csv.QUOTE_NONNUMERIC,
            3: csv.QUOTE_NONE,
        }[args.quoting]
    return kwargs


def open_file(path, encoding=None):
    f = io.open(path, mode='Ur', encoding=encoding)
    return f


if __name__ == '__main__':
    main()
