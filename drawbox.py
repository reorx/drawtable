# coding: utf-8

"""
┌─────┬─────┬─────┐
│ abc │ def │ ghi │
├─────┼─────┼─────┤
│  12 │   0 │ 1   │
├─────┼─────┼─────┤
│   4 │  72 │ 2   │
└─────┴─────┴─────┘


┌─────┬─────┬─────┐

│ abc │ def │ ghi │

├─────┼─────┼─────┤

│  12 │   0 │ 1   │

├─────┼─────┼─────┤

│   4 │  72 │ 2   │

└─────┴─────┴─────┘
"""


class BoxDrawer(object):
    align_marks = {
        'left': '<',
        'right': '>',
        'center': '^',
    }

    def __init__(self, margin_x=1, margin_y=0, align='left', col_max_width=16):
        self.margin_x = margin_x
        self.margin_x_str = ' ' * margin_x
        self.margin_y = margin_y
        self.align = align
        try:
            self.align_mark = self.align_marks[align]
        except KeyError:
            raise ValueError('align must be one of {}'.format(self.align_marks.keys()))
        self.col_max_width = col_max_width

    def preprocess_data(self, data):
        if not isinstance(data, list):
            raise TypeError('data must be list, get: {:r}'.format(data))
        cols = {}
        for row in data:
            if not isinstance(row, list):
                raise TypeError('row in data must be list, get: {:r}'.format(row))
            for index, i in enumerate(row):
                if not isinstance(i, str):
                    raise TypeError('item in row must be str, get: {:r}'.format(i))
                col = cols.setdefault(index, [])
                col.append(i)
        cols_width = {k: min([max(map(len, v)), self.col_max_width]) for k, v in cols.iteritems()}
        return cols, cols_width

    def _draw_line(self, row, cols_num, cols_width):
        cells = []
        for index in xrange(cols_num):
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
        n = self.col_max_width
        if not text:
            return ['']
        return [text[i:i + n] for i in range(0, len(text), n)]

    def draw_line(self, row, cols_num, cols_width):
        cols_split = {}
        max_items = 0
        for index in xrange(cols_num):
            try:
                i = row[index]
            except IndexError:
                i = ''
            sp = self._split_by_max_width(i)
            if len(sp) > max_items:
                max_items = len(sp)
            cols_split[index] = sp

        sub_rows = []
        for row_index in xrange(max_items):
            sub_row = []
            for col_index in xrange(cols_num):
                sp = cols_split[col_index]
                try:
                    sub_row.append(sp[row_index])
                except IndexError:
                    sub_row.append('')
            sub_rows.append(sub_row)
        sub_lines = [self._draw_line(r, cols_num, cols_width) for r in sub_rows]
        #print sub_rows, sub_lines, row
        return '\n'.join(sub_lines)

    def _cell_width(self, col_width):
        return self.margin_x * 2 + col_width

    def draw_top(self, cols_num, cols_width):
        """
        ┌─────┬─────┬─────┐
        """
        cells = []
        for index in xrange(cols_num):
            cells.append(self._cell_width(cols_width[index]) * '─')
        return '┌' + '┬'.join(cells) + '┐'

    def draw_sep(self, cols_num, cols_width):
        """
        ├─────┼─────┼─────┤
        """
        cells = []
        for index in xrange(cols_num):
            cells.append(self._cell_width(cols_width[index]) * '─')
        return '├' + '┼'.join(cells) + '┤'

    def draw_bottom(self, cols_num, cols_width):
        """
        └─────┴─────┴─────┘
        """
        cells = []
        for index in xrange(cols_num):
            cells.append(self._cell_width(cols_width[index]) * '─')
        return '└' + '┴'.join(cells) + '┘'

    def draw(self, data):
        """
        line:
        |<cell>|<cell>|...|

        cell:
        <margin-x><text><margin-x>
        """
        cols, cols_width = self.preprocess_data(data)
        cols_num = len(cols)
        margin_y_line = self._draw_line(['' for i in xrange(cols_num)], cols_num, cols_width)
        sep_line = self.draw_sep(cols_num, cols_width)

        lines = [self.draw_top(cols_num, cols_width)]

        row_last_index = len(data) - 1
        for row_index, row in enumerate(data):
            for _i in xrange(self.margin_y):
                lines.append(margin_y_line)
            lines.append(self.draw_line(row, cols_num, cols_width))
            for _i in xrange(self.margin_y):
                lines.append(margin_y_line)
            if row_index != row_last_index:
                lines.append(sep_line)

        lines.append(self.draw_bottom(cols_num, cols_width))

        for i in lines:
            print i


if __name__ == '__main__':
    import random
    import string

    def random_str(length):
        return ''.join(random.choice(string.ascii_letters) for i in xrange(length))

    def random_data():
        d = []
        for i in xrange(random.randint(1, 5)):
            d.append(
                [random_str(random.randint(0, 20)) for j in xrange(random.randint(1, 5))]
            )
        return d

    # one cell box
    BoxDrawer(margin_x=1, margin_y=0, col_max_width=40).draw([[
        ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
         'Ut enim ad minim veniam, quis nostrud exercitation.')
    ]])

    # complex box
    box = BoxDrawer(margin_x=2, margin_y=0, col_max_width=15, align='right')
    box.draw(random_data())
    box.draw([
        ['', ''],
        [''],
    ])
