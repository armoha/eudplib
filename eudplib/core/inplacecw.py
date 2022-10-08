#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Armoha

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

from ..utils import EPD
from .variable import IsEUDVariable, VProc
from .rawtrigger import (
    RawTrigger,
    SetMemory,
    SetTo,
    EncodePlayer,
    CurrentPlayer,
    SetDeaths,
)


def cpset(a, b):
    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        return a + b, RawTrigger
    elif IsEUDVariable(a) and IsEUDVariable(b):
        VProc(
            [a, b],
            [
                a.QueueAssignTo(EPD(0x6509B0)),
                b.QueueAddTo(EPD(0x6509B0)),
            ],
        )
    else:
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            a,
            [
                SetMemory(0x6509B0, SetTo, b),
                a.QueueAddTo(EPD(0x6509B0)),
            ],
        )
    from ..eudlib.memiof.modcurpl import f_setcurpl2cpcache

    return EncodePlayer(CurrentPlayer), f_setcurpl2cpcache


def iset(a, b, modifier, v):
    """f_dwwrite_epd(a + b, v)"""
    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        from ..eudlib.memiof.dwepdio import setdw_epd

        return setdw_epd(a + b, modifier, v)
    if IsEUDVariable(v):
        if IsEUDVariable(a) and IsEUDVariable(b):
            return VProc(
                [a, b, v],
                [
                    a.QueueAssignTo(EPD(v.getDestAddr())),
                    b.QueueAddTo(EPD(v.getDestAddr())),
                    v.SetModifier(modifier),
                ],
            )
        if IsEUDVariable(b):
            a, b = b, a
        return VProc(
            [a, v],
            [
                v.SetDest(b),
                a.QueueAddTo(EPD(v.getDestAddr())),
                v.SetModifier(modifier),
            ],
        )
    set_v = SetDeaths(0, modifier, v, 0)
    if IsEUDVariable(a) and IsEUDVariable(b):
        VProc(
            [a, b],
            [
                a.QueueAssignTo(EPD(set_v) + 4),
                b.QueueAddTo(EPD(set_v) + 4),
            ],
        )
    else:
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            a,
            [
                SetMemory(set_v + 16, SetTo, b),
                a.QueueAddTo(EPD(set_v) + 4),
            ],
        )
    return RawTrigger(actions=set_v)
