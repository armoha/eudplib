# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable
from typing import Any

from .. import core as c
from .. import trigger as tg
from .. import utils as ut
from ..localize import _


def DoActions(*actions, preserved=True) -> tuple[c.Forward, c.RawTrigger]:  # noqa: N802
    return tg.Trigger(actions=actions, preserved=preserved)


def EUDJump(nextptr, *, must_use=True) -> None:  # noqa: N802
    nt_list = ut.EUDGetLastBlockOfName("triggerscope")[1]["nexttrigger_list"]
    if must_use and not nt_list:
        raise ut.EPError(_("unreachable EUDJump"))
    if c.IsEUDVariable(nextptr):
        c.RawTrigger(
            nextptr=nextptr.GetVTable(),
            actions=nextptr.QueueAssignTo(ut.EPD(nextptr.GetVTable) + 1),
        )
    else:
        c.SetNextTrigger(nextptr)


def EUDJumpIf(conditions, ontrue) -> None:  # noqa: N802
    onfalse = c.Forward()
    tg.EUDBranch(conditions, ontrue, onfalse)
    onfalse << c.NextTrigger()


def EUDJumpIfNot(conditions, onfalse) -> None:  # noqa: N802
    ontrue = c.Forward()
    tg.EUDBranch(conditions, ontrue, onfalse)
    ontrue << c.NextTrigger()


def EUDTernary(  # noqa: N802
    conditions, *, neg=False
) -> Callable[[Any], Callable[[Any], c.EUDVariable]]:
    v = c.EUDVariable()
    t = c.Forward()
    end = c.Forward()

    if neg:
        EUDJumpIf(conditions, t)
    else:
        EUDJumpIfNot(conditions, t)

    def _1(ontrue):
        v << ontrue
        c.SetNextTrigger(end)
        t << c.NextTrigger()

        def _2(onfalse):
            v << onfalse
            end << c.NextTrigger()
            return v

        return _2

    return _1
