#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from eudplib import utils as ut

from .. import core as c
from .. import trigger as tg


def DoActions(*actions, preserved=True) -> tuple[c.Forward, c.RawTrigger]:
    return tg.Trigger(actions=actions, preserved=preserved)


def EUDJump(nextptr) -> None:
    if c.IsEUDVariable(nextptr):
        t = c.Forward()
        c.SeqCompute([(ut.EPD(t + 4), c.SetTo, nextptr)])
        t << c.RawTrigger()
    else:
        c.RawTrigger(nextptr=nextptr)


def EUDJumpIf(conditions, ontrue, *, _actions=None) -> None:
    onfalse = c.Forward()
    tg.EUDBranch(conditions, ontrue, onfalse, _actions=_actions)
    onfalse << c.NextTrigger()


def EUDJumpIfNot(conditions, onfalse, *, _actions=None) -> None:
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
