#!/usr/bin/python
from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ..memiof import f_getcurpl, f_setcurpl, f_setcurpl2cpcache
from ..utilf import (
    DisplayTextAll,
    PlayWAVAll,
    SetMissionObjectivesAll,
    f_getuserplayerid,
)
from .cpprint import FixedText, f_gettextptr
from .cpstr import GetMapStringAddr
from .fmtprint import _format_args
from .strbuffer import GetGlobalStringBuffer
from .strfunc import f_strlen_epd


def f_printAll(format_string, *args):
    if not args:
        return f_setcurpl2cpcache([], DisplayTextAll(format_string))
    oldcp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())
    gsb = GetGlobalStringBuffer()
    gsb.printf(format_string, *args)
    f_setcurpl(oldcp)


_display_text_all = DisplayTextAll(0)


@c.EUDFullFunc(
    [
        (ut.EPD(0x640B58), c.Add, 0, None),
        (ut.EPD(_display_text_all[1]) + 1, c.SetTo, 0, None),
    ],
    [None, c.TrgString],
)
def DisplayTextAllAt(line, text):
    with FixedText(_display_text_all):
        c.VProc([line, text], [])
        c.RawTrigger(
            conditions=c.Memory(0x640B58, c.AtLeast, 11),
            actions=c.SetMemory(0x640B58, c.Subtract, 11),
        )
    f_setcurpl2cpcache()


def f_printAllAt(line, format_string, *args):
    if not args:
        DisplayTextAllAt(line, format_string)
    oldcp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())
    gsb = GetGlobalStringBuffer()
    gsb.printfAt(line, format_string, *args)
    f_setcurpl(oldcp)
