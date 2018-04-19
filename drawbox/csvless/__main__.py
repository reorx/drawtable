#!/usr/bin/env python

import io
import csv
import argparse
import subprocess
from drawbox import Box, PY2


def main():
    """
    Render a CSV file in the console as a Markdown-compatible, fixed-width table.
    """
    parser = init_parser()

    args = parser.parse_args()

    f = open_file(args.file, encoding=args.encoding)
    reader = csv.reader(f, **get_reader_kwargs(args))

    box = Box(
        max_col_width=args.max_column_width,
        table_style=args.table_style,
    )

    less_cmd = ['less', '-S']
    if args.line_numbers:
        less_cmd.append('-N')

    p = subprocess.Popen(less_cmd, stdin=subprocess.PIPE)

    if PY2:
        def writer(line):
            p.stdin.write(line)
    else:
        def writer(line):
            p.stdin.write(line.encode())

    box.draw(reader, writer=writer)

    f.close()
    p.communicate()


def init_parser():
    # the `formatter_class` can make description & epilog show multiline
    parser = argparse.ArgumentParser(
        description='Render a CSV file in the console as a Markdown-compatible, fixed-width table.',
        epilog='',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # arguments
    parser.add_argument('file', metavar="FILE", type=str, help="csv file")

    # reader options
    parser.add_argument(
        '-d', '--delimiter', dest='delimiter',
        help='Delimiting character of the input CSV file.')
    parser.add_argument(
        '-b', '--no-doublequote', dest='doublequote', action='store_false',
        help='Whether or not double quotes are doubled in the input CSV file.')
    parser.add_argument(
        '-p', '--escapechar', dest='escapechar',
        help=('Character used to escape the delimiter if --quoting 3 ("Quote None") '
              'is specified and to escape the QUOTECHAR if --no-doublequote is specified.'))
    parser.add_argument(
        '-q', '--quotechar', dest='quotechar',
        help='Character used to quote strings in the input CSV file.')
    parser.add_argument(
        '-u', '--quoting', dest='quoting', type=int, choices=[0, 1, 2, 3],
        help=('Quoting style used in the input CSV file. 0 = Quote Minimal, '
              '1 = Quote All, 2 = Quote Non-numeric, 3 = Quote None.'))
    parser.add_argument(
        '-S', '--skipinitialspace', dest='skipinitialspace', action='store_true',
        help='Ignore whitespace immediately following the delimiter.')

    # file options
    parser.add_argument(
        '-e', '--encoding', dest='encoding', default='utf-8',
        help='Specify the encoding of the input CSV file.')

    # display options
    parser.add_argument(
        '--max-column-width', dest='max_column_width', type=int, default=32,
        help='Truncate all columns to at most this width. The remainder will be replaced with ellipsis.')
    parser.add_argument(
        '-H', '--no-header-row', dest='no_header_row', action='store_true',
        help=('Specify that the input CSV file has no header row. '
              'Will create default headers (a,b,c,...).'))
    parser.add_argument(
        '-N', '--linenumbers', dest='line_numbers', action='store_true',
        help='Show line numbers in the pager')
    parser.add_argument(
        '--table-style', dest='table_style', type=str, choices=['box', 'markdown'], default='base',
        help='')

    return parser


def get_reader_kwargs(args):
    """
    Extracts those from the command-line arguments those would should be passed through to the input CSV reader(s).
    """
    kwargs = {}

    for arg in ('delimiter', 'doublequote', 'escapechar', 'quotechar', 'quoting', 'skipinitialspace'):
        value = getattr(args, arg)
        if value is not None:
            kwargs[arg] = value
    return kwargs


def open_file(path, encoding=None):
    f = io.open(path, mode='Ur', encoding=encoding)
    return f


if __name__ == '__main__':
    main()
