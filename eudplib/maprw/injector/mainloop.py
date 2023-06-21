#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Callable

from ... import core as c
from ... import ctrlstru as cs
from ... import eudlib as sf
from ...core.eudfunc.trace.tracetool import _f_initstacktrace
from ...eudlib.stringf.locale import _detect_locale
from ...eudlib.stringf.tblprint import _f_initstattext
from ...eudlib.utilf.userpl import _f_initisusercp, _f_inituserplayerid
from ...localize import _
from ...utils import EPError, ep_assert

jumper: c.Forward | None = None
startFunctionList1: list[Callable] = []
startFunctionList2: list[Callable] = []
hasAlreadyStarted: int = 0


def _hasAlreadyStarted() -> bool:
    return hasAlreadyStarted == 2


def EUDOnStart(func: Callable) -> None:
    # FIXME: Callable[[], ...]
    ep_assert(
        hasAlreadyStarted < 2, "Can't use EUDOnStart here. See https://cafe.naver.com/edac/69262"
    )
    if hasAlreadyStarted == 0:
        startFunctionList1.append(func)
    else:
        _EUDOnStart2(func)


def _EUDOnStart2(func: Callable) -> None:
    startFunctionList2.append(func)


def _MainStarter(mf: Callable) -> c.Forward:
    global jumper, hasAlreadyStarted
    jumper = c.Forward()

    if c.PushTriggerScope():
        rootstarter = c.NextTrigger()

        # Various initializes
        _detect_locale()
        _f_inituserplayerid()
        _f_initisusercp()
        _f_initstacktrace()
        _f_initstattext()

        for func in startFunctionList1:
            func()
        hasAlreadyStarted = 1
        start2 = c.Forward()
        c.SetNextTrigger(start2)

        mf_start = c.NextTrigger()
        mf()

        hasAlreadyStarted = 2
        if startFunctionList2:
            c.PushTriggerScope()
            start2 << c.NextTrigger()
            for func in startFunctionList2:
                func()
            c.SetNextTrigger(mf_start)
            c.PopTriggerScope()
        else:
            start2 << mf_start

        c.RawTrigger(nextptr=0x80000000, actions=c.SetNextPtr(jumper, 0x80000000))
        jumper << c.RawTrigger(nextptr=rootstarter)

    c.PopTriggerScope()

    return jumper


def EUDDoEvents() -> None:
    if jumper is None:
        raise EPError(_("_MainStarter has not called"))
    oldcp = sf.f_getcurpl()

    _t = c.Forward()
    c.RawTrigger(
        nextptr=0x80000000,
        actions=c.SetNextPtr(jumper, _t),
    )
    _t << c.NextTrigger()

    sf.f_setcurpl(oldcp)
