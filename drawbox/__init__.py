# coding: utf-8

from __future__ import print_function
import sys
import collections


PY2 = sys.version_info.major == 2

if PY2:
    range = xrange  # NOQA


class BaseStyle(object):
    char_line_left = ''
    char_line_middle = ''
    char_line_right = ''

    has_sep = False
    has_footer = False

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(k, v)

        self.margin_y_str = None
        self.sep_str = None

    def prepare_margin_y(self, cells_width):
        charlen = sum(cells_width) + len(cells_width) + 1
        self.margin_y_str = self.char_line_left + charlen * ' ' + self.char_line_right

    def prepare_sep(self, cells_width):
        charlen = sum(cells_width) + len(cells_width) - 1
        self.sep_str = self.char_line_left + charlen * ' ' + self.char_line_right

    def draw_header(self, sub_row_cells_gen, cells_width):
        header = ''
        for sub_row_cells in sub_row_cells_gen:
            header += self.char_line_left + self.char_line_middle.join(sub_row_cells) + self.char_line_right + '\n'
        return header[:-1]

    def draw_line(self, cells_gen):
        return self.char_line_left + self.char_line_middle.join(cells_gen) + self.char_line_right

    def draw_footer(self, cells_width):
        charlen = sum(cells_width) + len(cells_width) - 1
        return self.char_line_left + charlen * ' ' + self.char_line_right


class BoxStyle(BaseStyle):
    char_line_left = '│'
    char_line_middle = '│'
    char_line_right = '│'

    has_sep = True
    has_footer = True

    def prepare_sep(self, cells_width):
        """
        ├─────┼─────┼─────┤
        """
        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '─')
        self.sep_str = '├' + '┼'.join(cells) + '┤'

    def draw_header(self, sub_row_cells_gen, cells_width):
        """
        ┌─────┬─────┬─────┐
        ├─────┼─────┼─────┤
        """
        lines = []

        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '─')
        lines.append('┌' + '┬'.join(cells) + '┐')

        for sub_row_cells in sub_row_cells_gen:
            lines.append(self.draw_line(sub_row_cells))

        lines.append(self.sep_str)
        return '\n'.join(lines)

    def draw_footer(self, cells_width):
        """
        └─────┴─────┴─────┘
        """
        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '─')
        return '└' + '┴'.join(cells) + '┘'


class MarkdownStyle(BaseStyle):
    char_line_left = '|'
    char_line_middle = '|'
    char_line_right = '|'

    def draw_header(self, sub_row_cells_gen, cells_width):
        """
        | xxx | ooo |
        | --- | --- |
        """
        lines = []

        for sub_row_cells in sub_row_cells_gen:
            lines.append(self.draw_line(sub_row_cells))

        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '-')
        lines.append(self.draw_line(cells))

        return '\n'.join(lines)


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

    def __init__(self, margin_x=1, margin_y=0, align='left', max_col_width=16, table_style='box'):
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

    def preprocess_data(self, data):
        if not isinstance(data, collections.Iterable):
            raise TypeError('data must be iterable, get: {:r}'.format(data))
        cols = {}
        rows = []
        rowslen = 0
        for row in data:
            rowslen += 1
            rows.append(row)
            if not isinstance(row, list):
                raise TypeError('row in data must be list, get: {:r}'.format(row))
            for index, i in enumerate(row):
                if not isinstance(i, str):
                    raise TypeError('item in row must be str, get: {:r}'.format(i))
                col = cols.setdefault(index, [])
                col.append(i)
        cols_width = {k: min([max(map(len, v)), self.max_col_width]) for k, v in cols.items()}
        return rows, rowslen, cols, cols_width

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
            if len(sp) > max_items:
                max_items = len(sp)
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

    def draw_row(self, sub_row_cells_gen):
        sub_lines = []
        for _i in range(self.margin_y):
            sub_lines.append(self.table_style.margin_y_str)

        for sub_row_cells in sub_row_cells_gen:
            sub_lines.append(
                self.table_style.draw_line(sub_row_cells)
            )

        for _i in range(self.margin_y):
            sub_lines.append(self.table_style.margin_y_str)

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

        rows, rowslen, cols, cols_width = self.preprocess_data(data)
        cols_num = len(cols)
        cells_width = [self.cell_width(cols_width[i]) for i in range(cols_num)]
        ts = self.table_style

        ts.prepare_margin_y(cells_width)
        ts.prepare_sep(cells_width)

        row_strs = []

        def append_and_write(row_str):
            row_strs.append(row_str)
            writer(row_str + '\n')

        row_last_index = rowslen - 1
        for row_index, row in enumerate(rows):
            sub_row_cells_gen = self.sub_row_cells_generator(row, cols_num, cols_width)

            if row_index == 0:
                append_and_write(ts.draw_header(sub_row_cells_gen, cells_width))
                continue

            append_and_write(self.draw_row(sub_row_cells_gen))
            if ts.has_sep and row_index != row_last_index:
                append_and_write(ts.sep_str)

        if ts.has_footer:
            append_and_write(ts.draw_footer(cells_width))


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
