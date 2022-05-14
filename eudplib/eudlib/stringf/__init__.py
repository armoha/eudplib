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

from .cpstr import GetMapStringAddr, CPString
from .dbstr import DBString

from .parse import f_parse
from .fmtprint import f_sprintf, f_sprintf_cp, f_eprintf, f_eprintAll

from .strbuffer import (
    StringBuffer,
    DisplayTextAt,
    GetGlobalStringBuffer,
    f_simpleprint,
    f_println,
    f_printAt,
)

from .strall import (
    f_printAll,
    DisplayTextAllAt,
    f_printAllAt,
)

from .strfunc import f_strcpy, f_strcmp, f_strlen, f_strlen_epd, f_strnstr

from .eudprint import (
    f_dbstr_adddw,
    f_dbstr_addptr,
    f_dbstr_addstr,
    f_dbstr_addstr_epd,
    ptr2s,
    epd2s,
    hptr,
    f_dbstr_print,
)

from .cpprint import (
    f_cpstr_adddw,
    f_cpstr_addptr,
    PColor,
    PName,
    f_cpstr_print,
    f_raise_CCMU,
    GetTBLAddr,
    f_eprintln,
    f_eprintln2,
    FixedText,
    f_gettextptr,
)

from .cputf8 import f_cp949_to_utf8_cpy
from .pname import SetPName, SetPNamef, IsPName
from .tblprint import f_settbl, f_settbl2, f_settblf, f_settblf2

from .texteffect import (
    f_cpchar_adddw,
    f_cpchar_print,
    TextFX_FadeIn,
    TextFX_FadeOut,
    TextFX_SetTimer,
    TextFX_Remove,
)
