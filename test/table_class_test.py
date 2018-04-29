import io
import random
import string
import pytest
from drawtable import Table


def random_str(length):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

def random_data():
    d = []
    for i in range(random.randint(1, 5)):
        d.append(
            [random_str(random.randint(0, 20)) for j in range(random.randint(1, 5))]
        )
    return d


@pytest.fixture
def writer():
    return io.StringIO()


def test_random_data(writer):
    box = Table(margin_x=2, margin_y=0, max_col_width=15, align='right', table_style='box')
    box.draw(random_data(), writer=writer.write)
    print(writer.getvalue())


def test_empty_box(writer):
    box = Table(margin_x=2, margin_y=0, max_col_width=15, align='right', table_style='box')
    box.draw([
        ['', ''],
        [''],
    ], writer=writer.write)
    want = """\
┌────┬────┐
│    │    │
├────┼────┤
│    │    │
└────┴────┘
"""
    assert writer.getvalue() == want


def test_one_cell_box(writer):
    # one cell box
    lorem = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

Sed ut perspiciatis,
unde omnis iste natus error
sit voluptatem accusantium doloremque laudantium,

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."""

    want = """\
┌──────────────────────────────────────────┐
│ Lorem ipsum dolor sit amet, consectetur  │
│ adipiscing elit, sed do eiusmod tempor i │
│ ncididunt ut labore et dolore magna aliq │
│ ua.                                      │
│ Ut enim ad minim veniam, quis nostrud ex │
│ ercitation ullamco laboris nisi ut aliqu │
│ ip ex ea commodo consequat.              │
│ Sed ut perspiciatis,                     │
│ unde omnis iste natus error              │
│ sit voluptatem accusantium doloremque la │
│ udantium,                                │
│ Duis aute irure dolor in reprehenderit i │
│ n voluptate velit esse cillum dolore eu  │
│ fugiat nulla pariatur.                   │
│ Excepteur sint occaecat cupidatat non pr │
│ oident, sunt in culpa qui officia deseru │
│ nt mollit anim id est laborum.           │
└──────────────────────────────────────────┘
"""
    Table(margin_x=1, margin_y=0, max_col_width=40, table_style='box').draw([[lorem]], writer=writer.write)
    assert writer.getvalue() == want
