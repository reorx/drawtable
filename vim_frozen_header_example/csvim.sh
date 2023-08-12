#!/bin/bash

vim -R -u NONE -N +'
map <right> 2zl
map <left> 2zh
map q :qa<CR>
set number scrollopt=hor scrollbind nowrap
1sp ./box-head.txt
2winc +
winc w
' ./box-body.txt
