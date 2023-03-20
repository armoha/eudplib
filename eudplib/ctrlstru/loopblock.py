#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Iterator
from typing import Any, Literal

from .. import core as c
from .. import utils as ut
from ..localize import _
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener


def _IsLoopBlock(block):
    return "contpoint" in block


# -------


def EUDInfLoop() -> CtrlStruOpener:
    def _footer() -> Literal[True]:
        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
        }

        ut.EUDCreateBlock("infloopblock", block)
        return True

    return CtrlStruOpener(_footer)


def EUDEndInfLoop() -> None:
    block = ut.EUDPopBlock("infloopblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << block["loopstart"]
    c.SetNextTrigger(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def EUDLoopN() -> CtrlStruOpener:
    def _footer(n: int) -> Literal[True]:
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


def EUDEndLoopN() -> None:
    block = ut.EUDPopBlock("loopnblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << c.NextTrigger()

    vardb = block["vardb"]
    c.RawTrigger(nextptr=block["loopstart"], actions=c.SetMemory(vardb, c.Subtract, 1))
    block["loopend"] << c.NextTrigger()


# -------


def EUDLoopRange(start, end=None) -> Iterator[c.EUDVariable]:
    ut.EUDCreateBlock("looprangeblock", None)
    if end is None:
        start, end = 0, start

    v = c.EUDVariable()
    v << start
    if EUDWhile()(v < end):
        block = ut.EUDPeekBlock("whileblock")[1]
        yield v
        if not block["contpoint"].IsSet():
            EUDLoopSetContinuePoint()
        v += 1
    EUDEndWhile()
    ut.EUDPopBlock("looprangeblock")


# -------


def EUDWhile() -> CtrlStruOpener:
    def _header() -> None:
        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
            "conditional": True,
        }

        ut.EUDCreateBlock("whileblock", block)

    def _footer(conditions, *, neg=False) -> Literal[True]:
        block = ut.EUDPeekBlock("whileblock")[1]
        if neg:
            EUDJumpIf(conditions, block["loopend"])
        else:
            EUDJumpIfNot(conditions, block["loopend"])
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


def EUDWhileNot() -> CtrlStruOpener:
    c = EUDWhile()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


def _UnsafeWhileNot() -> CtrlStruOpener:
    def _header() -> None:
        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
            "conditional": True,
        }

        ut.EUDCreateBlock("whileblock", block)

    def _footer(conditions) -> Literal[True]:
        block = ut.EUDPeekBlock("whileblock")[1]
        c.RawTrigger(
            conditions=conditions,
            actions=c.SetNextPtr(block["loopstart"], block["loopend"]),
        )
        block["conditional"] = False
        return True

    _header()
    return CtrlStruOpener(_footer)


def EUDEndWhile() -> None:
    block = ut.EUDPopBlock("whileblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << block["loopstart"]
    c.SetNextTrigger(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def _GetLastLoopBlock() -> tuple[str, Any]:
    for block in reversed(ut.EUDGetBlockList()):
        if _IsLoopBlock(block[1]):
            return block

    raise ut.EPError(_("No loop block surrounding this code area"))


def EUDLoopContinue() -> None:
    block = _GetLastLoopBlock()[1]
    EUDJump(block["contpoint"])


def EUDLoopContinueIf(conditions) -> None:
    block = _GetLastLoopBlock()[1]
    EUDJumpIf(conditions, block["contpoint"])


def EUDLoopContinueIfNot(conditions) -> None:
    block = _GetLastLoopBlock()[1]
    EUDJumpIfNot(conditions, block["contpoint"])


def EUDLoopIsContinuePointSet() -> bool:
    block = _GetLastLoopBlock()[1]
    return block["contpoint"].IsSet()


def EUDLoopSetContinuePoint() -> None:
    block = _GetLastLoopBlock()[1]
    block["contpoint"] << c.NextTrigger()


def EUDLoopBreak() -> None:
    block = _GetLastLoopBlock()[1]
    EUDJump(block["loopend"])


def EUDLoopBreakIf(conditions) -> None:
    block = _GetLastLoopBlock()[1]
    EUDJumpIf(conditions, block["loopend"])


def EUDLoopBreakIfNot(conditions) -> None:
    block = _GetLastLoopBlock()[1]
    EUDJumpIfNot(conditions, block["loopend"])
