#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from typing import TYPE_CHECKING, Literal

from ...localize import _
from ...utils import (
    EPError,
    EUDCreateBlock,
    EUDGetLastBlockOfName,
    EUDPopBlock,
    TriggerScopeError,
)
from ..allocator import ConstExpr, Forward


def PushTriggerScope() -> Literal[True]:
    EUDCreateBlock("triggerscope", {"nexttrigger_list": []})
    return True  # Allow `if PushTriggerScope()` syntax for indent


def SetNextTrigger(trg: ConstExpr) -> None:
    """For optimization purpose, one may call this function directly"""
    try:
        nt_list = EUDGetLastBlockOfName("triggerscope")[1]["nexttrigger_list"]
    except EPError as exc:
        raise TriggerScopeError(
            _("Must put Trigger into onPluginStart, beforeTriggerExec or afterTriggerExec")
        ) from exc
    for fw in nt_list:
        fw << trg
    nt_list.clear()


def NextTrigger() -> Forward:
    fw = Forward()
    try:
        nt_list = EUDGetLastBlockOfName("triggerscope")[1]["nexttrigger_list"]
    except EPError as exc:
        raise TriggerScopeError(
            _("Must put Trigger into onPluginStart, beforeTriggerExec or afterTriggerExec")
        ) from exc
    nt_list.append(fw)
    return fw


def _RegisterTrigger(trg: ConstExpr) -> None:
    SetNextTrigger(trg)


def PopTriggerScope() -> None:
    nt_list = EUDPopBlock("triggerscope")[1]["nexttrigger_list"]
    for fw in nt_list:
        fw << 0
