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
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener
from eudplib.localize import _


def _IsSwitchBlockId(idf):
    return idf == "swblock"


def EUDSwitch(var):
    block = {
        "targetvar": var,
        "casebrlist": {},
        "defaultbr": c.Forward(),
        "swend": c.Forward(),
    }

    c.PushTriggerScope()
    ut.EUDCreateBlock("swblock", block)

    return True


def EUDSwitchCase():
    def _footer(*numbers):
        for number in numbers:
            ut.ep_assert(
                isinstance(number, int) or isinstance(number, c.ConstExpr),
                _("Invalid selector start for EUDSwitch"),
            )

        lb = ut.EUDGetLastBlock()
        ut.ep_assert(lb[0] == "swblock", _("Block start/end mismatch"))
        block = lb[1]

        for number in numbers:
            ut.ep_assert(number not in block["casebrlist"], _("Duplicate cases"))
            block["casebrlist"][number] = c.NextTrigger()

        return True

    return CtrlStruOpener(_footer)


def EUDSwitchDefault():
    def _footer():
        lb = ut.EUDGetLastBlock()
        ut.ep_assert(lb[0] == "swblock", _("Block start/end mismatch"))
        block = lb[1]

        ut.ep_assert(not block["defaultbr"].IsSet(), _("Duplicate default"))
        block["defaultbr"] << c.NextTrigger()

        return True

    return CtrlStruOpener(_footer)


def EUDSwitchBreak():
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    EUDJump(block["swend"])


def EUDSwitchBreakIf(conditions):
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    EUDJumpIf(conditions, block["swend"])


def EUDSwitchBreakIfNot(conditions):
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    EUDJumpIfNot(conditions, block["swend"])


def EUDEndSwitch():
    lb = ut.EUDPopBlock("swblock")
    block = lb[1]
    swend = block["swend"]
    EUDJump(swend)  # Exit switch block
    c.PopTriggerScope()

    # If default block is not specified, skip it
    if not block["defaultbr"].IsSet():
        block["defaultbr"] << swend

    # Create key selector
    casebrlist = block["casebrlist"]
    defbranch = block["defaultbr"]
    casekeylist = sorted(block["casebrlist"].keys())
    var = block["targetvar"]

    def KeySelector(keys):
        # Uses simple binary search
        ret = c.NextTrigger()
        if len(keys) == 1:  # Only one keys on the list
            tg.EUDBranch(var == keys[0], casebrlist[keys[0]], defbranch)

        elif len(keys) >= 2:
            br1 = c.Forward()
            br2 = c.Forward()
            midpos = len(keys) // 2
            midval = keys[midpos]
            EUDJumpIf(var == midval, casebrlist[midval])
            tg.EUDBranch(var <= midval, br1, br2)
            br1 << KeySelector(keys[:midpos])
            br2 << KeySelector(keys[midpos + 1 :])

        else:  # len(keys) == 0
            return defbranch

        return ret

    KeySelector(casekeylist)

    swend << c.NextTrigger()
