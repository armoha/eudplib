#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable

from ... import core as c
from ... import eudlib as sf
from ...core.eudfunc.trace.tracetool import _f_initstacktrace
from ...eudlib.stringf.locale import _detect_locale
from ...eudlib.stringf.tblprint import _f_initstattext
from ...eudlib.utilf.userpl import _f_initisusercp, _f_inituserplayerid
from ...localize import _
from ...utils import EPError, ep_assert

_jumper: c.Forward | None = None
_start_functions1: list[Callable] = []
_start_functions2: list[Callable] = []
_has_already_started: int = 0


def has_already_started() -> bool:
    return _has_already_started == 2


def EUDOnStart(func: Callable) -> None:  # noqa: N802
    # FIXME: Callable[[], ...]
    ep_assert(
        _has_already_started < 2,
        "Can't use EUDOnStart here. See https://cafe.naver.com/edac/69262",
    )
    if _has_already_started == 0:
        _start_functions1.append(func)
    else:
        eud_onstart2(func)


def eud_onstart2(func: Callable) -> None:
    _start_functions2.append(func)


def main_starter(mf: Callable) -> c.Forward:
    global _jumper, _has_already_started
    _jumper = c.Forward()

    if c.PushTriggerScope():
        rootstarter = c.NextTrigger()

        # Various initializes
        _detect_locale()
        _f_inituserplayerid()
        _f_initisusercp()
        _f_initstacktrace()
        _f_initstattext()

        for func in _start_functions1:
            func()
        _has_already_started = 1
        start2 = c.Forward()
        c.SetNextTrigger(start2)

        mf_start = c.NextTrigger()
        mf()

        _has_already_started = 2
        if _start_functions2:
            c.PushTriggerScope()
            start2 << c.NextTrigger()
            for func in _start_functions2:
                func()
            c.SetNextTrigger(mf_start)
            c.PopTriggerScope()
        else:
            start2 << mf_start

        c.RawTrigger(nextptr=0x80000000, actions=c.SetNextPtr(_jumper, 0x80000000))
        _jumper << c.RawTrigger(nextptr=rootstarter)

    c.PopTriggerScope()

    return _jumper


def EUDDoEvents() -> None:  # noqa: N802
    if _jumper is None:
        raise EPError(_("main_starter has not called"))
    oldcp = sf.f_getcurpl()

    _t = c.Forward()
    c.RawTrigger(nextptr=0x80000000, actions=c.SetNextPtr(_jumper, _t))
    _t << c.NextTrigger()

    sf.f_setcurpl(oldcp)
