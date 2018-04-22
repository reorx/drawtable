# Drawtable (csvless)

Drawtable is a python library for drawing ASCII table with text data.
It also contains a command line tool called `csvless`
that helps you view csv files without hassle.

## Installation

```
pip install drawtable
```

## Usage

### CLI tool

For details please see `csvless -h`, here are some typical examples:

```
$ csvless samples/foo.csv

$ csvless -s markdown samples/foo.csv

$ csvless -s markdown --cat samples/foo.csv

$ csvless -s box -N samples/foo.csv

$ csvless -s box -N -n samples/foo.csv

$ csvless -H samples/foo.csv

$ csvless -w 10 --no-wrap samples/foo.csv
```

### Library

Draw table box for list data:

```python
>>> from drawbox import Table
>>> tb = Table(
...     margin_x=1,
...     margin_y=0,
...     align='left',
...     col_max_width=40,
... )
>>> tb.draw([
...     ['project', 'url'],
...     ['drawbox', 'https://github.com/reorx/drawbox'],
>>> ])
┌─────────┬──────────────────────────────────┐
│ project │ url                              │
├─────────┼──────────────────────────────────┤
│ drawbox │ https://github.com/reorx/drawbox │
└─────────┴──────────────────────────────────┘
```

Draw a simple one cell box:

```python
>>> from drawbox import Table
>>> tb = Table(
...     margin_x=1,
...     margin_y=0,
...     align='center',
...     col_max_width=40,
... )
>>> tb.draw([[
...     """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."""
... ]])
┌──────────────────────────────────────────┐
│ Lorem ipsum dolor sit amet, consectetur  │
│ adipiscing elit, sed do eiusmod tempor i │
│ ncididunt ut labore et dolore magna aliq │
│ ua. Ut enim ad minim veniam, quis nostru │
│ d exercitation ullamco laboris nisi ut a │
│     liquip ex ea commodo consequat.      │
└──────────────────────────────────────────┘
```
