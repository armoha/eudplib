#!/usr/bin/python
from .. import core as c
from .. import utils as ut
from ..core.eudfunc import EUDFullFunc
from ..eudlib.utilf.userpl import (
    DisplayTextAll,
    f_getuserplayerid,
)
from ..memio import f_getcurpl, f_setcurpl, f_setcurpl2cpcache
from .cpprint import FixedText
from .strbuffer import GetGlobalStringBuffer


def f_printAll(format_string, *args):  # noqa: N802
    if not args:
        return f_setcurpl2cpcache([], DisplayTextAll(format_string))
    oldcp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())
    gsb = GetGlobalStringBuffer()
    gsb.printf(format_string, *args)
    f_setcurpl(oldcp)


_display_text_all = DisplayTextAll(0)


@EUDFullFunc(
    [
        (ut.EPD(0x640B58), c.Add, 0, None),
        (ut.EPD(_display_text_all[1]) + 1, c.SetTo, 0, None),
    ],
    [None, c.TrgString],
)
def DisplayTextAllAt(line, text):  # noqa: N802
    with FixedText(_display_text_all):
        c.VProc([line, text], [])
        c.RawTrigger(
            conditions=c.Memory(0x640B58, c.AtLeast, 11),
            actions=c.SetMemory(0x640B58, c.Subtract, 11),
        )
    f_setcurpl2cpcache()


def f_printAllAt(line, format_string, *args):  # noqa: N802
    if not args:
        DisplayTextAllAt(line, format_string)
    oldcp = f_getcurpl()
    f_setcurpl(f_getuserplayerid())
    gsb = GetGlobalStringBuffer()
    gsb.printfAt(line, format_string, *args)
    f_setcurpl(oldcp)
