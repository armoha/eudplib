#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from .. import utils as ut
from ..localize import _
from . import loopblock as lb
from . import swblock as sb


def EUDContinue() -> None:
    return lb.EUDLoopContinue()


def EUDContinueIf(conditions) -> None:
    return lb.EUDLoopContinueIf(conditions)


def EUDContinueIfNot(conditions) -> None:
    return lb.EUDLoopContinueIfNot(conditions)


def EUDSetContinuePoint() -> None:
    return lb.EUDLoopSetContinuePoint()


def EUDIsContinuePointSet() -> bool:
    return lb.EUDLoopIsContinuePointSet()


# -------


def EUDBreak() -> None:
    for block in reversed(ut.EUDGetBlockList()):
        if lb._IsLoopBlock(block[1]):
            lb.EUDLoopBreak()
            return
        elif sb._IsSwitchBlockId(block[0]):
            sb.EUDSwitchBreak()
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))


def EUDBreakIf(conditions) -> None:
    for block in reversed(ut.EUDGetBlockList()):
        if lb._IsLoopBlock(block[1]):
            lb.EUDLoopBreakIf(conditions)
            return
        elif sb._IsSwitchBlockId(block[0]):
            sb.EUDSwitchBreakIf(conditions)
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))


def EUDBreakIfNot(conditions) -> None:
    for block in reversed(ut.EUDGetBlockList()):
        if lb._IsLoopBlock(block[1]):
            lb.EUDLoopBreakIfNot(conditions)
            return
        elif sb._IsSwitchBlockId(block[0]):
            sb.EUDSwitchBreakIfNot(conditions)
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))
