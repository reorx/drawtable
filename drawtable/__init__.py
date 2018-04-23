# coding: utf-8

from __future__ import print_function
import sys
import collections
import string
from drawtable.styles import BaseStyle, BoxStyle, MarkdownStyle, RstGridStyle


__version__ = '0.2.0'


PY2 = sys.version_info.major == 2

if PY2:
    range = xrange  # NOQA


auto_header_letters = string.ascii_uppercase
auto_header_letters_num = len(auto_header_letters)


# noinspection PyStringFormat
class Table(object):
    align_marks = {
        'left': '<',
        'right': '>',
        'center': '^',
    }

    table_styles = {
        'base': BaseStyle,
        'box': BoxStyle,
        'markdown': MarkdownStyle,
        'rst-grid': RstGridStyle,
    }

    # from `less`:
    # |_____XX_CONTENT|
    # explain:
    # `|` is the border of terminal window, `_` is space, `XX` is line number,
    # `CONTENT` is the actual value of the line
    row_number_width = 7

    def __init__(self, margin_x=1, margin_y=0, align='left',
                 max_col_width=16, table_style='box',
                 auto_header=False, row_numbers=False, wrap_row=True):
        self.margin_x = margin_x
        self.margin_x_str = ' ' * margin_x
        self.margin_y = margin_y
        self.align = align
        try:
            self.align_mark = self.align_marks[align]
        except KeyError:
            raise ValueError('align must be one of {}'.format(self.align_marks.keys()))
        self.max_col_width = max_col_width
        self.table_style = self.table_styles[table_style]()
        self.auto_header = auto_header
        self.row_numbers = row_numbers
        self.row_number_tmpl = '{:>' + str(self.row_number_width) + '} '
        self.row_number_empty = self.row_number_tmpl.format('')
        self.wrap_row = wrap_row

    @staticmethod
    def preprocess_data(data, has_header=True):
        if not isinstance(data, collections.Iterable):
            raise TypeError('data must be iterable, get: {:r}'.format(data))
        cols_width = {}
        header = []
        rows = []
        rowslen = 0
        count = 0
        for row in data:
            count += 1
            if has_header and count == 1:
                # skip append to rows
                header = row
                continue

            rowslen += 1
            rows.append(row)

            # if not isinstance(row, list):
            #     raise TypeError('row in data must be list, get: {:r}'.format(row))
            for index, i in enumerate(row):
                # if not isinstance(i, str):
                #    raise TypeError('item in row must be str, get: {:r}'.format(i))
                i_len = len(i)
                col_len = cols_width.setdefault(index, i_len)
                if i_len > col_len:
                    cols_width[index] = i_len
        return header, rows, rowslen, cols_width

    def sub_row_generator(self, row, cols_num, cols_width):
        """
        row: [
            'a very long line.',
            'short line',
            'a',
            '',
        ]

        cols_split:
        {
            0:          1:           2:     3:
            ['a very l' ['short li', ['a'], [''],
             'ong line'  'ne'],
             '.'],
        {

        sub_row(s):
        ['a very l', 'short', 'a', ''],
        ['ong line', 'ne', ''],
        ['.', '', ''],
        """
        # it's ok to define cols_split as `[]`, but `{}` is quicker in timeit result
        cols_split = {}
        max_items = 0
        for index in range(cols_num):
            try:
                i = row[index]
            except IndexError:
                i = ''
            sp = self._split_text(i)
            sp_len = len(sp)
            if sp_len > max_items:
                max_items = sp_len
            cols_split[index] = sp

        for sub_row_index in range(max_items):
            yield self.cell_generator_from_sub_row(sub_row_index, cols_split, cols_num, cols_width)

    def cell_generator_from_sub_row(self, sub_row_index, cols_split, cols_num, cols_width):
        for col_index in range(cols_num):
            sp = cols_split[col_index]
            try:
                v = sp[sub_row_index]
            except IndexError:
                v = ''
            tmpl = '{:' + self.align_mark + str(cols_width[col_index]) + '}'
            cell = self.margin_x_str + tmpl.format(v) + self.margin_x_str
            yield cell

    def cell_generator(self, values, cols_num, cols_width):
        for index in range(cols_num):
            col_width = cols_width[index]
            try:
                i = values[index]
            except IndexError:
                i = ''
            else:
                # truncate if too long
                i = truncate_str(i, col_width)
            tmpl = '{:' + self.align_mark + str(col_width) + '}'
            cell = self.margin_x_str + tmpl.format(i) + self.margin_x_str
            yield cell

    def _split_text(self, text):
        sp = []
        for i in text.split('\n'):
            if text:
                for j in range(0, len(i), self.max_col_width):
                    sp.append(i[j:j + self.max_col_width])
            else:
                sp.append(i)
        return sp

    def draw_row_str_from_sub_rows(self, sub_row_gen, row_num):
        sub_lines = []
        for _i in range(self.margin_y):
            sub_lines.append(self.format_line(self.table_style.margin_y_str))

        sub_row_count = 0
        for cell_gen in sub_row_gen:
            line = self.table_style.draw_line(cell_gen)
            if self.row_numbers and sub_row_count == 0:
                sub_lines.append(self.format_line_with_number(line, row_num))
            else:
                sub_lines.append(self.format_line(line))
            sub_row_count += 1

        for _i in range(self.margin_y):
            sub_lines.append(self.format_line(self.table_style.margin_y_str))

        return '\n'.join(sub_lines)

    def draw_row_str(self, cell_gen, row_num):
        sub_lines = []
        for _i in range(self.margin_y):
            sub_lines.append(self.format_line(self.table_style.margin_y_str))

        line = self.table_style.draw_line(cell_gen)
        if self.row_numbers:
            sub_lines.append(self.format_line_with_number(line, row_num))
        else:
            sub_lines.append(self.format_line(line))

        for _i in range(self.margin_y):
            sub_lines.append(self.format_line(self.table_style.margin_y_str))

        return '\n'.join(sub_lines)

    @staticmethod
    def get_auto_header_values(cols_num):
        vs = []
        for i in range(cols_num):
            if i < auto_header_letters_num:
                v = auto_header_letters[i]
            else:
                n = i % auto_header_letters_num
                v = auto_header_letters[n] + str(int(i / auto_header_letters_num))
            vs.append(v)
        return vs

    def format_lines(self, lines):
        return '\n'.join(self.format_line(i) for i in lines)

    def format_line(self, line):
        if self.row_numbers:
            return self.row_number_empty + line
        return line

    def format_line_with_number(self, line, num):
        return self.row_number_tmpl.format(num) + line

    def cell_width(self, col_width):
        return self.margin_x * 2 + col_width

    def draw(self, data, writer=None):
        """
        line:
        |<cell>|<cell>|...|

        cell:
        <margin-x><text><margin-x>
        """
        if writer is None:
            def writer(s):
                sys.stdout.write(s)

        has_header = True
        if self.auto_header:
            has_header = False
        header, rows, rowslen, cols_width = self.preprocess_data(data, has_header)
        if not has_header:
            header = self.get_auto_header_values(len(cols_width))

        # change cols_width according to:
        # 1. header
        # 2. config
        # 3. max_col_width
        for k, h in enumerate(header):
            h_len = len(h)
            cols_width[k] = min([max([cols_width.get(k, 0), h_len]), self.max_col_width])
        cols_num = len(cols_width)

        cells_width = [self.cell_width(cols_width[i]) for i in range(cols_num)]
        ts = self.table_style

        ts.prepare_margin_y(cells_width)
        ts.prepare_sep(cells_width)

        row_strs = []

        def append_and_write(row_str):
            row_strs.append(row_str)
            writer(row_str + '\n')

        # always wrap header even if `wrap_row` is false
        append_and_write(
            self.format_lines(
                ts.draw_header_lines(
                    self.sub_row_generator(header, cols_num, cols_width),
                    cells_width,
                    no_rows=rowslen == 0)
            )
        )

        row_num = 0

        if self.wrap_row:
            # wrap row hierarchy:
            #
            # row -> sub row generator
            #        |
            #        for-> cell generator
            #              |
            #              for-> cell
            for row in rows:
                row_num += 1
                sub_row_gen = self.sub_row_generator(row, cols_num, cols_width)

                append_and_write(self.draw_row_str_from_sub_rows(sub_row_gen, row_num))
                if ts.has_sep and row_num != rowslen:
                    append_and_write(self.format_line(ts.sep_str))
        else:
            # no wrap row hierarchy:
            #
            # row -> cell generator
            #        |
            #        for-> cell
            for row in rows:
                row_num += 1

                append_and_write(
                    self.draw_row_str(
                        self.cell_generator(row, cols_num, cols_width), row_num))
                if ts.has_sep and row_num != rowslen:
                    append_and_write(self.format_line(ts.sep_str))

        if ts.has_footer:
            append_and_write(self.format_line(ts.draw_footer(cells_width)))

        self.draw_result = {
            'row_num': row_num,
        }


ellipsis_str = '…'


def truncate_str(s, max_length):
    if len(s) > max_length:
        return s[:max_length - 1] + ellipsis_str
    return s


if __name__ == '__main__':
    import random
    import string

    def random_str(length):
        return ''.join(random.choice(string.ascii_letters) for i in range(length))

    def random_data():
        d = []
        for i in range(random.randint(1, 5)):
            d.append(
                [random_str(random.randint(0, 20)) for j in range(random.randint(1, 5))]
            )
        return d

    # complex box
    box = Table(margin_x=2, margin_y=0, max_col_width=15, align='right')
    box.draw(random_data())
    box.draw([
        ['', ''],
        [''],
    ])

    # one cell box
    lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Sed ut perspiciatis,
unde omnis iste natus error
sit voluptatem accusantium doloremque laudantium,

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""
    Table(margin_x=1, margin_y=0, max_col_width=40).draw([[lorem]])
