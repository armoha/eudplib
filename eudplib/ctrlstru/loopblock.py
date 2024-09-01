#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterator
from typing import Any, Literal

from .. import core as c
from .. import utils as ut
from ..localize import _
from .basicstru import EUDJump, EUDJumpIf, EUDJumpIfNot
from .cshelper import CtrlStruOpener


def _is_loopblock(block: dict[str, Any]) -> bool:
    return "contpoint" in block


# -------


def EUDInfLoop() -> CtrlStruOpener:  # noqa: N802
    def _footer() -> Literal[True]:
        block = {
            "loopstart": c.NextTrigger(),
            "loopend": c.Forward(),
            "contpoint": c.Forward(),
        }

        ut.EUDCreateBlock("infloopblock", block)
        return True

    return CtrlStruOpener(_footer)


def EUDEndInfLoop() -> None:  # noqa: N802
    block = ut.EUDPopBlock("infloopblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << block["loopstart"]
    c.SetNextTrigger(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def EUDLoopN() -> CtrlStruOpener:  # noqa: N802
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


def EUDEndLoopN() -> None:  # noqa: N802
    block = ut.EUDPopBlock("loopnblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << c.NextTrigger()

    vardb = block["vardb"]
    c.RawTrigger(nextptr=block["loopstart"], actions=c.SetMemory(vardb, c.Subtract, 1))
    block["loopend"] << c.NextTrigger()


# -------


def EUDLoopRange(start, end=None) -> Iterator[c.EUDVariable]:  # noqa: N802
    ut.EUDCreateBlock("looprangeblock", None)
    if end is None:
        start, end = 0, start

    v = c.EUDVariable()
    v << start
    if EUDWhile()(v < end):
        block = ut.EUDPeekBlock("whileblock")[1]
        yield v
        if not block["contpoint"].IsSet():
            set_continuepoint()
        v += 1
    EUDEndWhile()
    ut.EUDPopBlock("looprangeblock")


# -------


def EUDWhile() -> CtrlStruOpener:  # noqa: N802
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


def EUDWhileNot() -> CtrlStruOpener:  # noqa: N802
    c = EUDWhile()
    return CtrlStruOpener(lambda conditions: c(conditions, neg=True))


def _unsafe_whilenot() -> CtrlStruOpener:
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


def EUDEndWhile() -> None:  # noqa: N802
    block = ut.EUDPopBlock("whileblock")[1]
    if not block["contpoint"].IsSet():
        block["contpoint"] << block["loopstart"]
    c.SetNextTrigger(block["loopstart"])
    block["loopend"] << c.NextTrigger()


# -------


def _get_last_loopblock() -> tuple[str, Any]:
    for block in reversed(ut.EUDGetBlockList()):
        if _is_loopblock(block[1]):
            return block

    raise ut.EPError(_("No loop block surrounding this code area"))


def eudloop_continue() -> None:
    block = _get_last_loopblock()[1]
    try:
        EUDJump(block["contpoint"])
    except ut.EPError:
        ut.ep_warn(_("unreachable continue"))


def eudloop_continue_if(conditions) -> None:
    block = _get_last_loopblock()[1]
    EUDJumpIf(conditions, block["contpoint"])


def eudloop_continue_ifnot(conditions) -> None:
    block = _get_last_loopblock()[1]
    EUDJumpIfNot(conditions, block["contpoint"])


def is_continuepoint_set() -> bool:
    block = _get_last_loopblock()[1]
    return block["contpoint"].IsSet()


def set_continuepoint() -> None:
    block = _get_last_loopblock()[1]
    block["contpoint"] << c.NextTrigger()


def eudloop_break() -> None:
    block = _get_last_loopblock()[1]
    try:
        EUDJump(block["loopend"])
    except ut.EPError:
        ut.ep_warn(_("unreachable break"))


def eudloop_break_if(conditions) -> None:
    block = _get_last_loopblock()[1]
    EUDJumpIf(conditions, block["loopend"])


def eudloop_break_ifnot(conditions) -> None:
    block = _get_last_loopblock()[1]
    EUDJumpIfNot(conditions, block["loopend"])
