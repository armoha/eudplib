#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

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
