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

from ... import core as c, ctrlstru as cs, utils as ut
from . import dwepdio as dwm
from ...core.variable.evcommon import _ev
from .epddwio import f_dwepdread_cp


@c.EUDFunc
def _reader():
    ptr = c.EUDVariable()
    cs.DoActions(ptr.SetNumber(0))

    for i in ut.RandList(range(32)):
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** i),
            actions=ptr.AddNumber(2 ** i),
        )

    return ptr


def f_dwread_cp(cpo, **kwargs):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    ptr = _reader(**kwargs)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return ptr


def f_epdread_cp(cpo, **kwargs):
    ret = kwargs.get("ret")
    if ret is not None:
        ret.insert(0, _ev[4])
    return f_dwepdread_cp(cpo, **kwargs)[1]


@c.EUDFunc
def _wreader(subp):
    w = c.EUDVariable()
    w << 0
    cs.EUDSwitch(subp)
    for bits in ut.RandList(range(3)):
        cs.EUDSwitchCase()(bits)
        byte = 8 * bits
        for power in ut.RandList(range(byte, byte + 16)):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** power),
                actions=w.AddNumber(2 ** (power - byte)),
            )
        cs.EUDBreak()
    if cs.EUDSwitchCase()(3):
        for power in ut.RandList(range(24, 32)):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** power),
                actions=w.AddNumber(2 ** (power - 24)),
            )
        c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
        for power in ut.RandList(range(8)):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** power),
                actions=w.AddNumber(2 ** (power + 8)),
            )
        c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, -1))
        cs.EUDBreak()
    cs.EUDEndSwitch()
    return w


def f_wread_cp(cpo, subp):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    w = _wreader(subp)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return w


@c.EUDFunc
def _breader(subp):
    b = c.EUDVariable()
    b << 0
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(4)):
        cs.EUDSwitchCase()(i)
        for j in ut.RandList(range(8 * i, 8 * i + 8)):
            c.RawTrigger(
                conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** j),
                actions=b.AddNumber(2 ** (j - 8 * i)),
            )

        cs.EUDBreak()
    cs.EUDEndSwitch()
    return b


def f_bread_cp(cpo, subp):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    b = _breader(subp)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return b


def f_dwwrite_cp(cpo, value):
    cs.DoActions(
        [] if isinstance(cpo, int) and cpo == 0 else c.SetMemory(0x6509B0, c.Add, cpo),
        c.SetDeaths(c.CurrentPlayer, c.SetTo, value, 0),
        [] if isinstance(cpo, int) and cpo == 0 else c.SetMemory(0x6509B0, c.Add, -cpo),
    )


def f_dwadd_cp(cpo, value):
    cs.DoActions(
        [] if isinstance(cpo, int) and cpo == 0 else c.SetMemory(0x6509B0, c.Add, cpo),
        c.SetDeaths(c.CurrentPlayer, c.Add, value, 0),
        [] if isinstance(cpo, int) and cpo == 0 else c.SetMemory(0x6509B0, c.Add, -cpo),
    )


def f_dwsubtract_cp(cpo, value):
    cs.DoActions(
        [] if isinstance(cpo, int) and cpo == 0 else c.SetMemory(0x6509B0, c.Add, cpo),
        c.SetDeaths(c.CurrentPlayer, c.Subtract, value, 0),
        [] if isinstance(cpo, int) and cpo == 0 else c.SetMemory(0x6509B0, c.Add, -cpo),
    )


@c.EUDFunc
def _wwriter(subp, w):
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(3)):
        cs.EUDSwitchCase()(i)
        c.RawTrigger(
            actions=c.SetDeathsX(c.CurrentPlayer, c.SetTo, 0, 0, 65535 << (8 * i))
        )
        c.SeqCompute([(c.CurrentPlayer, c.Add, w * (256 ** i))])
        cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0, b1 = dwm.f_dwbreak(w)[2:4]
        f_bwrite_cp(0, 3, b0)
        f_bwrite_cp(1, 0, b1)

    cs.EUDEndSwitch()


def f_wwrite_cp(cpo, subp, w):
    try:
        cs.DoActions(
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeathsX(
                c.CurrentPlayer, c.SetTo, w * (256 ** subp), 0, 65535 << (8 * subp),
            ),
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, -cpo),
        )
    except (TypeError):
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
        _wwriter(subp, w)
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))


@c.EUDFunc
def _bwriter(subp, b):
    cs.EUDSwitch(subp)
    for i in ut.RandList(range(4)):
        cs.EUDSwitchCase()(i)
        c.RawTrigger(
            actions=c.SetDeathsX(c.CurrentPlayer, c.SetTo, 0, 0, 255 << (8 * i))
        )

        c.SeqCompute([(c.CurrentPlayer, c.Add, b * (256 ** i))])
        cs.EUDBreak()
    cs.EUDEndSwitch()
    return b


def f_bwrite_cp(cpo, subp, b):
    try:
        cs.DoActions(
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeathsX(
                c.CurrentPlayer, c.SetTo, b * (256 ** subp), 0, 255 << (8 * subp),
            ),
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, -cpo),
        )
    except (TypeError):
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
        _bwriter(subp, b)
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
