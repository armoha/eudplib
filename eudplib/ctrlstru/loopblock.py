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
from ..localize import _
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener


def _IsLoopBlock(block):
    return "contpoint" in block


# -------


def EUDInfLoop():
    def _footer():
        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
        }

        ut.EUDCreateBlock("infloopblock", block)
        return True

    return CtrlStruOpener(_footer)


def EUDEndInfLoop():
    block = ut.EUDPopBlock("infloopblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << block["loopstart"]
    EUDJump(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def EUDLoopN():
    def _footer(n):
        vardb = c.Db(4)
        c.RawTrigger(actions=c.SetMemory(vardb, c.SetTo, n))

        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
            "vardb": vardb,
        }

        ut.EUDCreateBlock("loopnblock", block)
        EUDJumpIf(c.Memory(vardb, c.Exactly, 0), block["loopend"])
        return True

    return CtrlStruOpener(_footer)


def EUDEndLoopN():
    block = ut.EUDPopBlock("loopnblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << c.NextTrigger()

    vardb = block["vardb"]
    c.RawTrigger(actions=c.SetMemory(vardb, c.Subtract, 1))
    EUDJump(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def EUDLoopRange(start, end=None):
    ut.EUDCreateBlock("looprangeblock", None)
    if end is None:
        start, end = 0, start

    v = c.EUDVariable()
    v << start
    if EUDWhile()(v < end):
        yield v
        EUDLoopSetContinuePoint()
        v += 1
    EUDEndWhile()
    ut.EUDPopBlock("looprangeblock")


# -------


def EUDWhile():
    def _header():
        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
            "conditional": True,
        }

        ut.EUDCreateBlock("whileblock", block)

    def _footer(conditions, *, neg=False):
        block = ut.EUDPeekBlock("whileblock")[1]
        if neg:
            EUDJumpIf(conditions, block["loopend"])
        else:
            EUDJumpIfNot(conditions, block["loopend"])
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


def EUDWhileNot():
    c = EUDWhile()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


def EUDEndWhile():
    block = ut.EUDPopBlock("whileblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << block["loopstart"]
    EUDJump(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def _GetLastLoopBlock():
    for block in reversed(ut.EUDGetBlockList()):
        if _IsLoopBlock(block[1]):
            return block

    raise ut.EPError(_("No loop block surrounding this code area"))


def EUDLoopContinue():
    block = _GetLastLoopBlock()[1]
    EUDJump(block["contpoint"])


def EUDLoopContinueIf(conditions):
    block = _GetLastLoopBlock()[1]
    EUDJumpIf(conditions, block["contpoint"])


def EUDLoopContinueIfNot(conditions):
    block = _GetLastLoopBlock()[1]
    EUDJumpIfNot(conditions, block["contpoint"])


def EUDLoopIsContinuePointSet():
    block = _GetLastLoopBlock()[1]
    return block["contpoint"].IsSet()


def EUDLoopSetContinuePoint():
    block = _GetLastLoopBlock()[1]
    block["contpoint"] << c.NextTrigger()


def EUDLoopBreak():
    block = _GetLastLoopBlock()[1]
    EUDJump(block["loopend"])


def EUDLoopBreakIf(conditions):
    block = _GetLastLoopBlock()[1]
    EUDJumpIf(conditions, block["loopend"])


def EUDLoopBreakIfNot(conditions):
    block = _GetLastLoopBlock()[1]
    EUDJumpIfNot(conditions, block["loopend"])
