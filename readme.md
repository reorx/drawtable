# Drawbox

Draw ASCII art box with text.

## Usage

Draw table box to show data:

```python
>>> from drawbox import Box
>>> box = Box(
...     margin_x=1,
...     margin_y=0,
...     align='left',
...     col_max_width=40,
... )
>>> box.draw([
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
>>> from drawbox import Box
>>> box = Box(
...     margin_x=1,
...     margin_y=0,
...     align='center',
...     col_max_width=40,
... )
>>> box.draw([[
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
