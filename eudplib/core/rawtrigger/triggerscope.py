#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal

from ...localize import _
from ...utils import (
    EPError,
    EUDCreateBlock,
    EUDGetLastBlockOfName,
    EUDPopBlock,
    TriggerScopeError,
)
from ..allocator import ConstExpr, Forward

# fmt: off
_ERR = _("Must put Trigger into onPluginStart, beforeTriggerExec or afterTriggerExec")  # noqa: E501
# fmt: on


def PushTriggerScope() -> Literal[True]:  # noqa: N802
    EUDCreateBlock("triggerscope", {"nexttrigger_list": []})
    return True  # Allow `if PushTriggerScope()` syntax for indent


def SetNextTrigger(trg: ConstExpr) -> None:  # noqa: N802
    """For optimization purpose, one may call this function directly"""
    try:
        nt_list = EUDGetLastBlockOfName("triggerscope")[1]["nexttrigger_list"]
    except EPError as exc:
        raise TriggerScopeError(_ERR) from exc
    for fw in nt_list:
        fw << trg
    nt_list.clear()


def NextTrigger() -> Forward:  # noqa: N802
    fw = Forward()
    try:
        nt_list = EUDGetLastBlockOfName("triggerscope")[1]["nexttrigger_list"]
    except EPError as exc:
        raise TriggerScopeError(_ERR) from exc
    nt_list.append(fw)
    return fw


def _register_trigger(trg: ConstExpr) -> None:
    SetNextTrigger(trg)


def PopTriggerScope() -> None:  # noqa: N802
    nt_list = EUDPopBlock("triggerscope")[1]["nexttrigger_list"]
    for fw in nt_list:
        fw << 0
