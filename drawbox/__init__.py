# coding: utf-8

from __future__ import print_function
import sys
import collections
import string
from drawbox.styles import BaseStyle, BoxStyle, MarkdownStyle


PY2 = sys.version_info.major == 2

if PY2:
    range = xrange  # NOQA


auto_header_letters = string.ascii_uppercase
auto_header_letters_num = len(auto_header_letters)


class Box(object):
    align_marks = {
        'left': '<',
        'right': '>',
        'center': '^',
    }

    table_styles = {
        'base': BaseStyle,
        'box': BoxStyle,
        'markdown': MarkdownStyle,
    }

    # from `less`:
    # |_____XX_CONTENT|
    # explain:
    # `|` is the border of terminal window, `_` is space, `XX` is line number,
    # `CONTENT` is the actual value of the line
    row_number_width = 7

    def __init__(self, margin_x=1, margin_y=0, align='left',
                 max_col_width=16, table_style='box',
                 auto_header=False, row_numbers=False):
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

    def preprocess_data(self, data, has_header=True):
        if not isinstance(data, collections.Iterable):
            raise TypeError('data must be iterable, get: {:r}'.format(data))
        cols = {}
        header = None
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

            #if not isinstance(row, list):
            #    raise TypeError('row in data must be list, get: {:r}'.format(row))
            for index, i in enumerate(row):
                if not isinstance(i, str):
                    raise TypeError('item in row must be str, get: {:r}'.format(i))
                col = cols.setdefault(index, [])
                col.append(i)
        cols_width = {k: min([max(map(len, v)), self.max_col_width]) for k, v in cols.items()}
        return header, rows, rowslen, cols, cols_width

    def cells_generator(self, values, cols_num, cols_width):
        for index in range(cols_num):
            try:
                i = values[index]
            except IndexError:
                i = ''
            width = cols_width[index]
            tmpl = '{:' + self.align_mark + str(width) + '}'
            text = tmpl.format(i)
            cell = self.margin_x_str + text + self.margin_x_str
            yield cell

    def cell_width(self, col_width):
        return self.margin_x * 2 + col_width

    def sub_row_cells_generator(self, row, cols_num, cols_width):
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

        for row_index in range(max_items):
            sub_row = []
            for col_index in range(cols_num):
                sp = cols_split[col_index]
                try:
                    sub_row.append(sp[row_index])
                except IndexError:
                    sub_row.append('')
            yield self.cells_generator(sub_row, cols_num, cols_width)

    def draw_row(self, sub_row_cells_gen, row_num):
        sub_lines = []
        for _i in range(self.margin_y):
            sub_lines.append(self.format_line(self.table_style.margin_y_str))

        sub_row_count = 0
        for sub_row_cells in sub_row_cells_gen:
            line = self.table_style.draw_line(sub_row_cells)
            if self.row_numbers and sub_row_count == 0:
                sub_lines.append(self.format_line_with_number(line, row_num))
            else:
                sub_lines.append(self.format_line(line))
            sub_row_count += 1

        for _i in range(self.margin_y):
            sub_lines.append(self.format_line(self.table_style.margin_y_str))

        #print(sub_lines, row)
        return '\n'.join(sub_lines)

    def _split_by_max_width(self, text):
        n = self.max_col_width
        if not text:
            return ['']
        return [text[i:i + n] for i in range(0, len(text), n)]

    def _split_text(self, text):
        sp = []
        for i in text.split('\n'):
            sp += self._split_by_max_width(i)
        return sp

    def get_auto_header_values(self, cols_num, cols_width):
        vs = []
        for i in range(cols_num):
            if i < auto_header_letters_num:
                v = auto_header_letters[i]
            else:
                n = i % auto_header_letters_num
                v = auto_header_letters[n] + str(int(i / auto_header_letters_num))
            vs.append(v)
        return vs

    def format_row_str(self, row_str, row_num=''):
        if self.row_numbers:
            return self.row_number_tmpl.format(row_num) + row_str
        return row_str

    def format_lines(self, lines):
        return '\n'.join(self.format_line(i) for i in lines)

    def format_line(self, line):
        if self.row_numbers:
            return self.row_number_empty + line
        return line

    def format_line_with_number(self, line, num):
        return self.row_number_tmpl.format(num) + line

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
        header, rows, rowslen, cols, cols_width = self.preprocess_data(data, has_header)
        cols_num = len(cols)
        if not has_header:
            header = self.get_auto_header_values(cols_num, cols_width)

        # change cols_width according to header
        for k, v in cols_width.items():
            h_len = len(header[k])
            if h_len > v:
                cols_width[k] = h_len

        cells_width = [self.cell_width(cols_width[i]) for i in range(cols_num)]
        ts = self.table_style

        ts.prepare_margin_y(cells_width)
        ts.prepare_sep(cells_width)

        row_strs = []

        def append_and_write(row_str):
            row_strs.append(row_str)
            writer(row_str + '\n')

        append_and_write(
            self.format_lines(
                ts.draw_header_lines(
                    self.sub_row_cells_generator(header, cols_num, cols_width),
                    cells_width)
            )
        )

        row_last_index = rowslen - 1
        for row_index, row in enumerate(rows):
            row_num = row_index + 1
            sub_row_cells_gen = self.sub_row_cells_generator(row, cols_num, cols_width)

            append_and_write(self.draw_row(sub_row_cells_gen, row_num))
            if ts.has_sep and row_index != row_last_index:
                append_and_write(self.format_line(ts.sep_str))

        if ts.has_footer:
            append_and_write(self.format_line(ts.draw_footer(cells_width)))

        self.draw_result = {
            'row_num': row_num,
        }


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
    box = Box(margin_x=2, margin_y=0, max_col_width=15, align='right')
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
    Box(margin_x=1, margin_y=0, max_col_width=40).draw([[lorem]])
