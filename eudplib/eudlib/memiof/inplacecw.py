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

from . import dwepdio as dwm
from eudplib import core as c, utils as ut


def iset(a, b, modifier, v):
    """f_dwwrite_epd(a + b, v)"""
    if not (c.IsEUDVariable(a) or c.IsEUDVariable(b)):
        return dwm.setdw_epd(a + b, modifier, v)
    if c.IsEUDVariable(v):
        if c.IsEUDVariable(a) and c.IsEUDVariable(b):
            return c.VProc(
                [a, b, v],
                [
                    a.QueueAssignTo(ut.EPD(v.getDestAddr())),
                    b.QueueAddTo(ut.EPD(v.getDestAddr())),
                    v.SetModifier(modifier),
                ],
            )
        if c.IsEUDVariable(b):
            a, b = b, a
        return c.VProc(
            [a, v],
            [
                v.SetDest(b),
                a.QueueAddTo(ut.EPD(v.getDestAddr())),
                v.SetModifier(modifier),
            ],
        )
    set_v = c.SetDeaths(0, modifier, v, 0)
    if c.IsEUDVariable(a) and c.IsEUDVariable(b):
        c.VProc(
            [a, b],
            [
                a.QueueAssignTo(ut.EPD(set_v)),
                b.QueueAddTo(ut.EPD(set_v)),
            ],
        )
    else:
        if c.IsEUDVariable(b):
            a, b = b, a
        c.VProc(
            a,
            [
                c.SetMemory(set_v + 4, c.SetTo, b),
                a.QueueAddTo(ut.EPD(set_v) + 1),
            ],
        )
    return c.RawTrigger(actions=set_v)
