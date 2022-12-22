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
from ... import eudlib as sf
from ...core.eudfunc.trace.tracetool import _f_initstacktrace
from ...eudlib.utilf.userpl import _f_initisusercp
from ...utils import ep_assert

jumper = None
startFunctionList1 = []
startFunctionList2 = []
hasAlreadyStarted = 0


def _hasAlreadyStarted():
    return hasAlreadyStarted == 2


def EUDOnStart(func):
    ep_assert(
        hasAlreadyStarted < 2, "Can't use EUDOnStart here. See https://cafe.naver.com/edac/69262"
    )
    if hasAlreadyStarted == 0:
        startFunctionList1.append(func)
    else:
        _EUDOnStart2(func)


def _EUDOnStart2(func):
    startFunctionList2.append(func)


def _MainStarter(mf):
    global jumper, hasAlreadyStarted
    jumper = c.Forward()

    if c.PushTriggerScope():
        rootstarter = c.NextTrigger()

        # Various initializes
        _f_initisusercp()
        sf.f_getcurpl()
        _f_initstacktrace()

        hasAlreadyStarted = 1
        for func in startFunctionList1:
            func()
        start2 = c.Forward()
        c.SetNextTrigger(start2)

        mf_start = c.NextTrigger()
        mf()

        hasAlreadyStarted = 2
        if startFunctionList2:
            c.PushTriggerScope()
            start2 << c.NextTrigger()
            for func in startFunctionList2:
                func()
            c.SetNextTrigger(mf_start)
            c.PopTriggerScope()
        else:
            start2 << mf_start

        c.RawTrigger(nextptr=0x80000000, actions=c.SetNextPtr(jumper, 0x80000000))
        jumper << c.RawTrigger(nextptr=rootstarter)

    c.PopTriggerScope()

    return jumper


def EUDDoEvents():
    oldcp = sf.f_getcurpl()

    _t = c.Forward()
    cs.DoActions(c.SetNextPtr(jumper, _t))
    cs.EUDJump(0x80000000)
    _t << c.NextTrigger()

    sf.f_setcurpl(oldcp)
