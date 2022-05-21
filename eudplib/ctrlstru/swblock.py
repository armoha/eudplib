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
from .jumptable import JumpTriggerForward
from eudplib.localize import _
from itertools import chain, combinations


def _IsSwitchBlockId(idf):
    return idf == "swblock"


def EPDSwitch(epd, mask=0xFFFFFFFF):
    epd = c.EncodePlayer(epd)
    block = {
        "targetepd": epd,
        "bitmask": mask,
        "casebrlist": {},
        "defaultbr": c.Forward(),
        "swend": c.Forward(),
    }

    c.PushTriggerScope()
    ut.EUDCreateBlock("swblock", block)

    return True


def EUDSwitch(var, mask=0xFFFFFFFF):
    block = {
        "targetvar": var,
        "bitmask": mask,
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
            ut.ep_assert(number & block["bitmask"] == number, _("cases out of mask"))
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

    bitmask = block["bitmask"]
    casebrlist = block["casebrlist"]
    defbranch = block["defaultbr"]
    casekeylist = sorted(block["casebrlist"].keys())
    try:
        epd = ut.EPD(block["targetvar"].getValueAddr())
    except KeyError:
        epd = block["targetepd"]
    except AttributeError:
        # constant value switch
        if block["targetvar"] in casekeylist:
            c.SetNextTrigger(casebrlist[block["targetvar"]])
        else:
            c.SetNextTrigger(defbranch)
        swend << c.NextTrigger()
        return

    if not casekeylist:
        swend << c.NextTrigger()
        return

    keyand, keyor = casekeylist[0], 0
    for key in casekeylist:
        keyand &= key
        keyor |= key
    keyxor = keyor - keyand
    keybits = list(ut.bits(keyxor))

    def powerset(iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

    keylist = sorted(map(sum, powerset(ut.bits(keyxor))))
    density = len(casebrlist) / len(keylist)
    if density >= 0.4:
        # use JumpTable
        check_invariant = c.MemoryXEPD(
            epd, c.Exactly, keyand, (~keyor | keyand) & bitmask
        )
        EUDJumpIfNot(check_invariant, defbranch)

        jump_table = JumpTriggerForward(
            [casebrlist.get(keyand + key, defbranch) for key in keylist]
        )
        jumper = c.Forward()

        if c.IsEUDVariable(epd):
            epd = c.EncodePlayer(c.CurrentPlayer)
            epdvar = block["targetepd"]
            cpcache = c.curpl.GetCPCache()
            c.VProc(
                epdvar,
                [
                    cpcache.SetDest(ut.EPD(0x6509B0)),
                    epdvar.QueueAssignTo(ut.EPD(0x6509B0)),
                    c.SetNextPtr(jumper, jump_table),
                ],
            )
        else:
            lastbit = c.RawTrigger(actions=c.SetNextPtr(jumper, jump_table))

        for i, bit in enumerate(keybits):
            lastbit = c.RawTrigger(
                conditions=c.MemoryXEPD(epd, c.AtLeast, 1, bit),
                actions=c.SetMemory(jumper + 4, c.Add, 20 * (1 << i)),
            )

        if c.IsEUDVariable(epd):
            jumper << cpcache.GetVTable()
            c.SetNextTrigger(cpcache.GetVTable())
        else:
            jumper << lastbit
    else:
        # use binary search
        pass

    swend << c.NextTrigger()
