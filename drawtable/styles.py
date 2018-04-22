# coding: utf-8


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

    def draw_header_lines(self, sub_row_cells_gen, cells_width, no_rows=False):
        lines = []
        for sub_row_cells in sub_row_cells_gen:
            lines.append(self.char_line_left + self.char_line_middle.join(sub_row_cells) + self.char_line_right)
        return lines

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

    def draw_header_lines(self, sub_row, cells_width, no_rows=False):
        """
        ┌─────┬─────┬─────┐
        ├─────┼─────┼─────┤
        """
        lines = []

        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '─')
        lines.append('┌' + '┬'.join(cells) + '┐')

        for cells_gen in sub_row:
            lines.append(self.draw_line(cells_gen))

        if not no_rows:
            lines.append(self.sep_str)
        return lines

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

    def draw_header_lines(self, sub_row_cells_gen, cells_width, no_rows=False):
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

        return lines


class RstGridStyle(BaseStyle):
    char_line_left = '|'
    char_line_middle = '|'
    char_line_right = '|'
    has_sep = True
    has_footer = True

    def prepare_sep(self, cells_width):
        """
        +------------+------------+-----------+
        """
        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '-')
        self.sep_str = '+' + '+'.join(cells) + '+'

    def draw_header_lines(self, sub_row_cells_gen, cells_width, no_rows=False):
        """
        +------------+------------+-----------+
        | Header 1   | Header 2   | Header 3  |
        +============+============+===========+
        """
        lines = []

        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '-')
        lines.append('+' + '+'.join(cells) + '+')

        for sub_row_cells in sub_row_cells_gen:
            lines.append(self.draw_line(sub_row_cells))

        cells = []
        for cell_width in cells_width:
            cells.append(cell_width * '-')
        lines.append('+' + '+'.join(cells) + '+')
        return lines

    def draw_footer(self, cells_width):
        """
        +------------+------------+-----------+
        """
        return self.sep_str
