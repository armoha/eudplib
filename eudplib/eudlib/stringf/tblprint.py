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


class _StatTxtTblEncoding:
    encoding = "cp949"


def f_settbl(tblID, offset, *args, encoding=None):
    args = ut.FlattenList(args)
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = _StatTxtTblEncoding.encoding

    if encoding.casefold() == "UTF-8".casefold():
        if isinstance(args[-1], str):
            if args[-1][-1] != "\u2009":
                args[-1] = args[-1] + "\u2009"
        else:
            args.append("\u2009")

    return f_dbstr_print(dst, *args, encoding=encoding)


def f_settbl2(tblID, offset, *args, encoding=None):
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = _StatTxtTblEncoding.encoding

    return f_dbstr_print(dst, *args, EOS=False, encoding=encoding)


def f_settblf(tblID, offset, format_string, *args, encoding=None):
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = _StatTxtTblEncoding.encoding

    if encoding.casefold() == "UTF-8".casefold() and format_string[-1] != "\u2009":
        format_string += "\u2009"

    return f_sprintf(dst, format_string, *args, encoding=encoding)


def f_settblf2(tblID, offset, format_string, *args, encoding=None):
    dst = GetTBLAddr(tblID)
    dst += offset

    if encoding is None:
        encoding = _StatTxtTblEncoding.encoding

    return f_sprintf(dst, format_string, *args, EOS=False, encoding=encoding)
