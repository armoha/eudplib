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

from eudplib import core as c, utils as ut, ctrlstru as cs

from ..memiof import f_dwread_epd

_localcp = None
_cpbranch = None


def f_getuserplayerid():
    global _localcp
    if _localcp is None:
        if cs.EUDExecuteOnce()():
            _localcp = f_dwread_epd(ut.EPD(0x512684))
        cs.EUDEndExecuteOnce()
    return _localcp


def CPBranch(ontrue, onfalse):
    global _cpbranch
    if _cpbranch is None:
        c.PushTriggerScope()
        _cpbranch = c.Forward()
        _cpbranch << c.RawTrigger(
            nextptr=0, conditions=LocalCP(), actions=c.SetNextPtr(_cpbranch, 0)
        )
        c.PopTriggerScope()

    c.RawTrigger(
        nextptr=_cpbranch,
        actions=[
            c.SetNextPtr(_cpbranch, onfalse),
            c.SetMemory(_cpbranch + 348, c.SetTo, ontrue),
        ],
    )


class ReadInit:
    def __init__(self, dst, src):
        self._dst = ut.EPD(dst)
        self._src = ut.EPD(src)


def LocalCP():
    ret = c.Memory(0x6509B0, c.Exactly, 0)
    ReadInit(ret + 16, 0x512684)
    return
