# coding: utf-8

from __future__ import print_function
import sys


PY2 = sys.version_info.major == 2

if PY2:
    range = xrange  # NOQA


class Box(object):
    align_marks = {
        'left': '<',
        'right': '>',
        'center': '^',
    }

    def __init__(self, margin_x=1, margin_y=0, align='left', max_col_width=16):
        self.margin_x = margin_x
        self.margin_x_str = ' ' * margin_x
        self.margin_y = margin_y
        self.align = align
        try:
            self.align_mark = self.align_marks[align]
        except KeyError:
            raise ValueError('align must be one of {}'.format(self.align_marks.keys()))
        self.max_col_width = max_col_width

    def preprocess_data(self, data):
        #if not isinstance(data, list):
        #    raise TypeError('data must be list, get: {:r}'.format(data))
        cols = {}
        rows = []
        datalen = 0
        for row in data:
            datalen += 1
            rows.append(row)
            if not isinstance(row, list):
                raise TypeError('row in data must be list, get: {:r}'.format(row))
            for index, i in enumerate(row):
                if not isinstance(i, str):
                    raise TypeError('item in row must be str, get: {:r}'.format(i))
                col = cols.setdefault(index, [])
                col.append(i)
        cols_width = {k: min([max(map(len, v)), self.max_col_width]) for k, v in cols.items()}
        return rows, cols, cols_width, datalen

    def _draw_line(self, row, cols_num, cols_width):
        cells = []
        for index in range(cols_num):
            try:
                i = row[index]
            except IndexError:
                i = ''
            width = cols_width[index]
            tmpl = '{:' + self.align_mark + str(width) + '}'
            text = tmpl.format(i)
            cell = self.margin_x_str + text + self.margin_x_str
            cells.append(cell)
        cells = [''] + cells + ['']
        line = '│'.join(cells)
        return line

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

    def draw_line(self, row, cols_num, cols_width):
        cols_split = {}
        max_items = 0
        for index in range(cols_num):
            try:
                i = row[index]
            except IndexError:
                i = ''
            sp = self._split_text(i)
            if len(sp) > max_items:
                max_items = len(sp)
            cols_split[index] = sp

        sub_rows = []
        for row_index in range(max_items):
            sub_row = []
            for col_index in range(cols_num):
                sp = cols_split[col_index]
                try:
                    sub_row.append(sp[row_index])
                except IndexError:
                    sub_row.append('')
            sub_rows.append(sub_row)
        sub_lines = [self._draw_line(r, cols_num, cols_width) for r in sub_rows]
        #print(sub_rows, sub_lines, row)
        return '\n'.join(sub_lines)

    def _cell_width(self, col_width):
        return self.margin_x * 2 + col_width

    def draw_top(self, cols_num, cols_width):
        """
        ┌─────┬─────┬─────┐
        """
        cells = []
        for index in range(cols_num):
            cells.append(self._cell_width(cols_width[index]) * '─')
        return '┌' + '┬'.join(cells) + '┐'

    def draw_sep(self, cols_num, cols_width):
        """
        ├─────┼─────┼─────┤
        """
        cells = []
        for index in range(cols_num):
            cells.append(self._cell_width(cols_width[index]) * '─')
        return '├' + '┼'.join(cells) + '┤'

    def draw_bottom(self, cols_num, cols_width):
        """
        └─────┴─────┴─────┘
        """
        cells = []
        for index in range(cols_num):
            cells.append(self._cell_width(cols_width[index]) * '─')
        return '└' + '┴'.join(cells) + '┘'

    def draw(self, data, writer=None):
        """
        line:
        |<cell>|<cell>|...|

        cell:
        <margin-x><text><margin-x>
        """
        rows, cols, cols_width, datalen = self.preprocess_data(data)
        cols_num = len(cols)
        margin_y_line = self._draw_line(['' for i in range(cols_num)], cols_num, cols_width)
        sep_line = self.draw_sep(cols_num, cols_width)

        lines = [self.draw_top(cols_num, cols_width)]

        row_last_index = datalen - 1
        for row_index, row in enumerate(rows):
            for _i in range(self.margin_y):
                lines.append(margin_y_line)
            lines.append(self.draw_line(row, cols_num, cols_width))
            for _i in range(self.margin_y):
                lines.append(margin_y_line)
            if row_index != row_last_index:
                lines.append(sep_line)

        lines.append(self.draw_bottom(cols_num, cols_width))

        if writer is None:
            def writer(s):
                sys.stdout.write(s)

        for i in lines:
            writer(i + '\n')


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
