#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from .cpprint import (
    FixedText,
    PColor,
    PName,
    f_cpstr_adddw,
    f_cpstr_addptr,
    f_cpstr_print,
    f_eprintln,
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
from .tblprint import (
    GetTBLAddr,
    StatText,
    f_eprintln2,
    f_settbl,
    f_settbl2,
    f_settblf,
    f_settblf2,
)
from .texteffect import (
    TextFX_FadeIn,
    TextFX_FadeOut,
    TextFX_Remove,
    TextFX_SetTimer,
    f_cpchar_adddw,
    f_cpchar_print,
)
