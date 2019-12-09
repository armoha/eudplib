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

from . import (
    dwepdio as dwm,
    cpmemio as cpm,
    byterw as brw,
    bwepdio as bwm,
    modcurpl as cp,
)
from ..rwcommon import br1, bw1
from ... import core as c, ctrlstru as cs, utils as ut

# Helper functions

_br = br1
_bw = bw1


def _ptr2epd(ptr):
    if ut.isUnproxyInstance(ptr, c.EUDVariable):
        epd, subp = c.f_div(ptr + (-0x58A364), 4)
    else:
        dst = ptr + (-0x58A364)
        epd, subp = dst // 4, dst % 4
    return epd, subp


def f_dwwrite(ptr, dw):
    if type(ptr) == int and ptr % 4 == 0:
        dwm.f_dwwrite_epd(ut.EPD(ptr), dw)
    else:
        chars = dwm.f_dwbreak(dw)[2:]
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
    for i in ut.RandList(range(1, 4)):
        cs.EUDSwitchCase()(i)

        for j in ut.RandList(range(8 * i, 32)):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** j),
                actions=dw.AddNumber(2 ** (j - 8 * i)),
            )

        c.SeqCompute([(ut.EPD(0x6509B0), c.Add, 1)])

        for j in ut.RandList(range(8 * i)):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** j),
                actions=dw.AddNumber(2 ** (j + 32 - 8 * i)),
            )

        cs.EUDBreak()

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return dw


def f_dwread(ptr):
    if type(ptr) == int and ptr % 4 == 0:
        return dwm.f_dwread_epd(ut.EPD(ptr))
    else:
        return _dwread(ptr)


def f_wread(ptr):
    epd, subp = _ptr2epd(ptr)
    return bwm.f_wread_epd(epd, subp)


def f_bread(ptr):
    epd, subp = _ptr2epd(ptr)
    return bwm.f_bread_epd(epd, subp)
