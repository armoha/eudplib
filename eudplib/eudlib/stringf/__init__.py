#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

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

from .cpprint import (
    FixedText,
    GetTBLAddr,
    PColor,
    PName,
    f_cpstr_adddw,
    f_cpstr_addptr,
    f_cpstr_print,
    f_eprintln,
    f_eprintln2,
    f_gettextptr,
    f_raise_CCMU,
)
from .cpstr import CPString, GetMapStringAddr
from .cputf8 import f_cp949_to_utf8_cpy
from .dbstr import DBString
from .eudprint import (
    epd2s,
    f_dbstr_adddw,
    f_dbstr_addptr,
    f_dbstr_addstr,
    f_dbstr_addstr_epd,
    f_dbstr_print,
    hptr,
    ptr2s,
)
from .fmtprint import f_eprintAll, f_eprintf, f_sprintf, f_sprintf_cp
from .parse import f_parse
from .pname import IsPName, SetPName, SetPNamef
from .strall import DisplayTextAllAt, f_printAll, f_printAllAt
from .strbuffer import (
    DisplayTextAt,
    GetGlobalStringBuffer,
    StringBuffer,
    f_printAt,
    f_println,
    f_simpleprint,
)
from .strfunc import f_strcmp, f_strcpy, f_strlen, f_strlen_epd, f_strnstr
from .tblprint import f_settbl, f_settbl2, f_settblf, f_settblf2
from .texteffect import (
    TextFX_FadeIn,
    TextFX_FadeOut,
    TextFX_Remove,
    TextFX_SetTimer,
    f_cpchar_adddw,
    f_cpchar_print,
)
