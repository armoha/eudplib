#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from .cpprint import GetTBLAddr
from .eudprint import f_dbstr_print
from .fmtprint import f_sprintf


def f_settbl(tblID, offset, *args, encoding="cp949"):
    dst = GetTBLAddr(tblID)
    dst += offset
    if encoding.casefold() == "UTF-8".casefold():
        f_dbstr_print(dst, *args, "\u2009", encoding="UTF-8")
    else:
        f_dbstr_print(dst, *args, encoding=encoding)


def f_settbl2(tblID, offset, *args, encoding="cp949"):
    dst = GetTBLAddr(tblID)
    dst += offset
    f_dbstr_print(dst, *args, EOS=False, encoding=encoding)


def f_settblf(tblID, offset, format_string, *args, encoding="cp949"):
    dst = GetTBLAddr(tblID)
    dst += offset
    if encoding.casefold() == "UTF-8".casefold() and format_string[-1] != "\u2009":
        format_string += "\u2009"
    f_sprintf(dst, format_string, *args, encoding=encoding)


def f_settblf2(tblID, offset, format_string, *args, encoding="cp949"):
    dst = GetTBLAddr(tblID)
    dst += offset
    f_sprintf(dst, format_string, *args, EOS=False, encoding=encoding)
