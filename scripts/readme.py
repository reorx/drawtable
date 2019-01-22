from drawtable import Table


if __name__ == '__main__':
    tb = Table(
        margin_x=1,
        margin_y=0,
        align='left',
        max_col_width=40,
    )
    tb.draw([
        ['project', 'url'],
        ['drawtable', 'https://github.com/reorx/drawtable'],
    ])


    tb1 = Table(
        margin_x=1,
        margin_y=0,
        align='center',
        max_col_width=40,
    )
    tb1.draw([[
        """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."""
    ]])
