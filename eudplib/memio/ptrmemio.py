#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from . import bwepdio as bwm
from . import cpmemio as cpm
from . import dwepdio as dwm
from . import modcurpl as cp


def _ptr2epd(ptr):
    if c.IsEUDVariable(ptr):
        epd, subp = c.f_div(ptr + (-0x58A364), 4)
    else:
        epd, subp = divmod(ptr + (-0x58A364), 4)
    return epd, subp


def f_dwwrite(ptr, dw):
    if isinstance(ptr, int) and ptr % 4 == 0:
        dwm.f_dwwrite_epd(ut.EPD(ptr), dw)
    else:
        chars = dwm.f_dwbreak(dw)[2:]
        from .rwcommon import bw1

        _bw = bw1
        _bw.seekoffset(ptr)
        _bw.writebyte(chars[0])
        _bw.writebyte(chars[1])
        _bw.writebyte(chars[2])
        _bw.writebyte(chars[3])


def f_wwrite(ptr, w):
    epd, subp = _ptr2epd(ptr)
    bwm.f_wwrite_epd(epd, subp, w)


def f_bwrite(ptr, b):
    epd, subp = _ptr2epd(ptr)
    bwm.f_bwrite_epd(epd, subp, b)


# -----------------------------


@c.EUDFunc
def _dwread(ptr):
    ptr -= 0x58A364
    dw, subp = c.EUDCreateVariables(2)
    c.f_div(ptr, 4, ret=[ut.EPD(0x6509B0), subp])
    dw << 0  # TODO: merge this action to f_div call trigger
    cs.EUDSwitch(subp)

    # Case 0
    if cs.EUDSwitchCase()(0):
        cpm.f_dwread_cp(0, ret=[dw])
        cs.EUDBreak()

    # Else → Complex
    for i in ut._rand_lst(range(1, 4)):
        cs.EUDSwitchCase()(i)

        for j in ut._rand_lst(range(8 * i, 32)):
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**j),
                actions=dw.AddNumber(2 ** (j - 8 * i)),
            )

        c.SeqCompute([(ut.EPD(0x6509B0), c.Add, 1)])

        for j in ut._rand_lst(range(8 * i)):
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**j),
                actions=dw.AddNumber(2 ** (j + 32 - 8 * i)),
            )

        cs.EUDBreak()

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return dw


def f_dwread(ptr, **kwargs):
    if (isinstance(ptr, int) and ptr % 4 == 0) or (
        not c.IsEUDVariable(ptr)
        and isinstance(ptr, (c.RlocInt_C, c.ConstExpr))  # noqa: UP038
        and ptr._is_aligned_ptr()
    ):
        return dwm.f_dwread_epd(ut.EPD(ptr), **kwargs)
    else:
        return _dwread(ptr, **kwargs)


def f_wread(ptr, **kwargs):
    return bwm.f_wread_epd(*_ptr2epd(ptr), **kwargs)


def f_bread(ptr, **kwargs):
    return bwm.f_bread_epd(*_ptr2epd(ptr), **kwargs)
