#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from ... import core as c, ctrlstru as cs, utils as ut
from .cpprint import GetTBLAddr
from .eudprint import f_dbstr_print
from .fmtprint import f_sprintf


def f_settbl(tblID, offset, *args):
    dst = GetTBLAddr(tblID)
    dst += offset
    f_dbstr_print(dst, *args, encoding="cp949")


def f_settbl2(tblID, offset, *args):
    dst = GetTBLAddr(tblID)
    dst += offset
    f_dbstr_print(dst, *args, EOS=False, encoding="cp949")


def f_settblf(tblID, offset, format_string, *args):
    dst = GetTBLAddr(tblID)
    dst += offset
    f_sprintf(dst, format_string, *args, encoding="cp949")


def f_settblf2(tblID, offset, format_string, *args):
    dst = GetTBLAddr(tblID)
    dst += offset
    f_sprintf(dst, format_string, *args, EOS=False, encoding="cp949")
