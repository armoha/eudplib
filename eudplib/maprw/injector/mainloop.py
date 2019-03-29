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
from ...eudlib.stringf.strbuffer import _f_initstrbuffer


jumper = None
startFunctionList = []


def EUDOnStart(func):
    startFunctionList.append(func)


def _MainStarter(mf):
    global jumper
    jumper = c.Forward()

    if c.PushTriggerScope():
        rootstarter = c.NextTrigger()

        # Various initializes
        _f_initstrbuffer()
        sf.f_getcurpl()
        _f_initstacktrace()

        for func in startFunctionList:
            func()

        mf()

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
