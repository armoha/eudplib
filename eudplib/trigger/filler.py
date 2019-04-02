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

from .. import core as c
from .. import utils as ut


def _dww(dstepd, v):
    act = c.Forward()
    c.SeqCompute(((ut.EPD(act + 16), c.SetTo, dstepd), (ut.EPD(act + 20), c.SetTo, v)))
    c.RawTrigger(actions=(act << c.SetMemory(0, c.SetTo, 0)))


def _filldw(dstepd, v1):
    c.SeqCompute(((dstepd, c.SetTo, v1),))


@c.EUDFunc
def _fillwbb(dstepd, v1, v2, v3):
    ret = c.EUDVariable()
    c.VProc(v1, [
        v1.QueueAssignTo(ret),
        v1.SetNumberX(0, 0xFFFF0000),
    ])

    for i in range(7, -1, -1):
        c.RawTrigger(
            conditions=v2.AtLeastX(1, 2 ** i),
            actions=ret.AddNumber(2 ** (i + 16)),
        )

    for i in range(7, -1, -1):
        c.RawTrigger(
            conditions=v3.AtLeastX(1, 2 ** i),
            actions=ret.AddNumber(2 ** (i + 24)),
        )

    _dww(dstepd, ret)


@c.EUDFunc
def _fillbbbb(dstepd, v1, v2, v3, v4):
    ret = c.EUDVariable()
    c.VProc(v1, [
        v1.QueueAssignTo(ret),
        v1.SetNumberX(0, 0xFFFFFF00),
    ])

    vlist = (v2, v3, v4)
    for i, v in enumerate(vlist):
        i += 1
        lsf = 8 * i
        for i in range(7, -1, -1):
            c.RawTrigger(
                conditions=v.AtLeastX(1, 2 ** i),
                actions=ret.AddNumber(2 ** (i + lsf)),
            )

    _dww(dstepd, ret)
