#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import utils as ut
from ..localize import _
from . import loopblock as lb
from . import swblock as sb


def EUDContinue() -> None:  # noqa: N802
    return lb.eudloop_continue()


def EUDContinueIf(conditions) -> None:  # noqa: N802
    return lb.eudloop_continue_if(conditions)


def EUDContinueIfNot(conditions) -> None:  # noqa: N802
    return lb.eudloop_continue_ifnot(conditions)


def EUDSetContinuePoint() -> None:  # noqa: N802
    return lb.set_continuepoint()


def EUDIsContinuePointSet() -> bool:  # noqa: N802
    return lb.is_continuepoint_set()


# -------


def EUDBreak() -> None:  # noqa: N802
    for block in reversed(ut.EUDGetBlockList()):
        if lb._is_loopblock(block[1]):
            lb.eudloop_break()
            return
        elif sb._is_switch_blockid(block[0]):
            sb.eudswitch_break()
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))


def EUDBreakIf(conditions) -> None:  # noqa: N802
    for block in reversed(ut.EUDGetBlockList()):
        if lb._is_loopblock(block[1]):
            lb.eudloop_break_if(conditions)
            return
        elif sb._is_switch_blockid(block[0]):
            sb.eudswitch_break_if(conditions)
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))


def EUDBreakIfNot(conditions) -> None:  # noqa: N802
    for block in reversed(ut.EUDGetBlockList()):
        if lb._is_loopblock(block[1]):
            lb.eudloop_break_ifnot(conditions)
            return
        elif sb._is_switch_blockid(block[0]):
            sb.eudswitch_break_ifnot(conditions)
            return

    raise ut.EPError(_("No loop/switch block surrounding this code area"))
