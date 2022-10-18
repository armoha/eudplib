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

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from . import byterw as brw
from . import cpmemio as cpm
from . import dwepdio as dwm
from . import modcurpl as cp

# Helper functions


def _lshift(a, b):
    if c.IsEUDVariable(a):
        return c.f_bitlshift(a, b)
    if isinstance(b, int) and b == 0:
        return a
    return a << b


@c.EUDFunc
def _wwriter(epd, subp, w):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(3)):
        if cs.EUDSwitchCase()(i):
            cs.DoActions(
                c.SetDeathsX(c.CurrentPlayer, c.SetTo, _lshift(w, 8 * i), 0, 0xFFFF << (8 * i))
            )
            cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0, b1 = dwm.f_dwbreak(w)[2:4]
        cpm.f_bwrite_cp(0, 3, b0)
        cpm.f_bwrite_cp(1, 0, b1)

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()


def f_wwrite_epd(epd, subp, w):
    if type(subp) is int:
        if subp == 3:
            return _wwriter(epd, subp, w)

        try:
            cs.DoActions(c.SetDeathsX(epd, c.SetTo, _lshift(w, 8 * subp), 0, 0xFFFF << (8 * subp)))
        except (TypeError):
            _wwriter(epd, subp, w)
    else:
        _wwriter(epd, subp, w)


@c.EUDFunc
def _bwriter(epd, subp, b):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(4)):
        if cs.EUDSwitchCase()(i):
            cs.DoActions(
                c.SetDeathsX(c.CurrentPlayer, c.SetTo, _lshift(b, 8 * i), 0, 0xFF << (8 * i))
            )
            cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return b


def f_bwrite_epd(epd, subp, b):
    try:
        cs.DoActions(c.SetDeathsX(epd, c.SetTo, _lshift(b, 8 * subp), 0, 0xFF << (8 * subp)))
    except (TypeError):
        _bwriter(epd, subp, b)


# -----------------------------


@c.EUDFunc
def f_wread_epd(epd, subp):
    w = c.EUDVariable()
    c.VProc(epd, [epd.SetDest(ut.EPD(0x6509B0)), w.SetNumber(0)])
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(3)):
        if cs.EUDSwitchCase()(i):
            for j in ut.RandList(range(8 * i, 8 * i + 16)):
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2**j),
                    actions=w.AddNumber(2 ** (j - 8 * i)),
                )

            cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0 = cpm.f_bread_cp(0, 3)
        b1 = cpm.f_bread_cp(1, 0)
        w << b0 + b1 * 256

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return w


@c.EUDFunc
def f_bread_epd(epd, subp):
    b = c.EUDVariable()
    c.VProc(epd, [epd.SetDest(ut.EPD(0x6509B0)), b.SetNumber(0)])
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(4)):
        if cs.EUDSwitchCase()(i):
            for j in ut.RandList(range(8 * i, 8 * i + 8)):
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2**j),
                    actions=b.AddNumber(2 ** (j - 8 * i)),
                )

            cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return b


def f_maskwrite_epd(epd, value, mask):
    cs.DoActions(c.SetDeathsX(epd, c.SetTo, value, 0, mask))
