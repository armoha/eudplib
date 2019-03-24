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

from . import dwepdio as dwm, cpmemio as cpm, byterw as brw, modcurpl as cp
from ... import core as c, ctrlstru as cs, utils as ut

# Helper functions


@c.EUDFunc
def _wwriter(epd, subp, w):
    oldcp = cp.f_getcurpl()
    cp.f_setcurpl(epd)
    cs.EUDSwitch(subp)
    for i in range(3):
        cs.EUDSwitchCase()(i)
        c.RawTrigger(
            actions=c.SetDeathsX(c.CurrentPlayer, c.SetTo, 0, 0, 65535 * 2 ** (8 * i))
        )
        c.SeqCompute([(c.CurrentPlayer, c.Add, w * (256 ** i))])
        cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0, b1 = dwm.f_dwbreak(w)[2:4]
        cpm.f_bwrite_cp(0, 3, b0)
        cpm.f_bwrite_cp(1, 0, b1)

    cs.EUDEndSwitch()
    cp.f_setcurpl(oldcp)


def f_wwrite_epd(epd, subp, w):
    if type(subp) is int:
        if subp == 3:
            return _wwriter(epd, subp, w)

        try:
            cs.DoActions(
                c.SetDeathsX(epd, c.SetTo, w << (8 * subp), 0, 0xffff << (8 * subp))
            )
        except (TypeError):
            _wwriter(epd, subp, w)
    else:
        _wwriter(epd, subp, w)


@c.EUDFunc
def _bwriter(epd, subp, b):
    oldcp = cp.f_getcurpl()
    cp.f_setcurpl(epd)
    cs.EUDSwitch(subp)
    for i in range(4):
        cs.EUDSwitchCase()(i)
        c.RawTrigger(
            actions=c.SetDeathsX(c.CurrentPlayer, c.SetTo, 0, 0, 255 * 2 ** (8 * i))
        )
        c.SeqCompute([(c.CurrentPlayer, c.Add, b * (256 ** i))])
        cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl(oldcp)
    return b


def f_bwrite_epd(epd, subp, b):
    try:
        cs.DoActions(
            c.SetDeathsX(epd, c.SetTo, b * (256 ** subp), 0, 255 * 2 ** (8 * subp))
        )
    except (TypeError):
        _bwriter(epd, subp, b)


# -----------------------------


@c.EUDFunc
def f_wread_epd(epd, subp):
    oldcp = cp.f_getcurpl()
    w = c.EUDVariable()
    cs.DoActions([c.SetCurrentPlayer(epd), w.SetNumber(0)])
    cs.EUDSwitch(subp)
    for i in range(3):
        cs.EUDSwitchCase()(i)
        for j in range(8 * (i + 2) - 1, 8 * i - 1, -1):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** j),
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
    cp.f_setcurpl(oldcp)
    return w


@c.EUDFunc
def f_bread_epd(epd, subp):
    oldcp = cp.f_getcurpl()
    b = c.EUDVariable()
    cs.DoActions([c.SetCurrentPlayer(epd), b.SetNumber(0)])
    cs.EUDSwitch(subp)
    for i in range(4):
        cs.EUDSwitchCase()(i)
        for j in range(8 * (i + 1) - 1, 8 * i - 1, -1):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** j),
                actions=b.AddNumber(2 ** (j - 8 * i)),
            )

        cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl(oldcp)
    return b
