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

from . import loopblock as lb, swblock as sb

from .. import utils as ut
from ..localize import _


def EUDContinue():
    return lb.EUDLoopContinue()


def EUDContinueIf(conditions):
    return lb.EUDLoopContinueIf(conditions)


def EUDContinueIfNot(conditions):
    return lb.EUDLoopContinueIfNot(conditions)


def EUDSetContinuePoint():
    return lb.EUDLoopSetContinuePoint()


def EUDIsContinuePointSet():
    return lb.EUDLoopIsContinuePointSet()


# -------


def EUDBreak():
    for block in reversed(ut.EUDGetBlockList()):
        if lb._IsLoopBlock(block[1]):
            lb.EUDLoopBreak()
            return
        elif sb._IsSwitchBlockId(block[0]):
            sb.EUDSwitchBreak()
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))


def EUDBreakIf(conditions):
    for block in reversed(ut.EUDGetBlockList()):
        if lb._IsLoopBlock(block[1]):
            lb.EUDLoopBreakIf(conditions)
            return
        elif sb._IsSwitchBlockId(block[0]):
            sb.EUDSwitchBreakIf(conditions)
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))


def EUDBreakIfNot(conditions):
    for block in reversed(ut.EUDGetBlockList()):
        if lb._IsLoopBlock(block[1]):
            lb.EUDLoopBreakIfNot(conditions)
            return
        elif sb._IsSwitchBlockId(block[0]):
            sb.EUDSwitchBreakIfNot(conditions)
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))
