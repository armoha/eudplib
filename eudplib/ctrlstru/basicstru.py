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
from .. import trigger as tg
from eudplib import utils as ut


def DoActions(*actions, preserved=True):
    tg.Trigger(actions=actions, preserved=preserved)


def EUDJump(nextptr):
    if isinstance(nextptr, c.EUDVariable):
        t = c.Forward()
        c.SeqCompute([(ut.EPD(t + 4), c.SetTo, nextptr)])
        t << c.RawTrigger()
    else:
        c.RawTrigger(nextptr=nextptr)


def EUDJumpIf(conditions, ontrue, *, _actions=None):
    onfalse = c.Forward()
    tg.EUDBranch(conditions, ontrue, onfalse, _actions=_actions)
    onfalse << c.NextTrigger()


def EUDJumpIfNot(conditions, onfalse, *, _actions=None):
    ontrue = c.Forward()
    tg.EUDBranch(conditions, ontrue, onfalse, _actions=_actions)
    ontrue << c.NextTrigger()


def EUDTernary(conditions, *, neg=False):
    v = c.EUDVariable()
    t = c.Forward()
    end = c.Forward()

    if neg:
        EUDJumpIf(conditions, t)
    else:
        EUDJumpIfNot(conditions, t)

    def _1(ontrue):
        v << ontrue
        EUDJump(end)
        t << c.NextTrigger()

        def _2(onfalse):
            v << onfalse
            end << c.NextTrigger()
            return v

        return _2

    return _1
