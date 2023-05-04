#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


import types
from typing import Any

from ... import core as c
from ... import ctrlstru as cs
from ... import eudlib as sf
from ... import trigger as t
from ... import utils as ut
from ...core import RawTrigger
from .btInliner import tStartEnd

_inlineGlobals = {}


def ComputeBaseInlineCodeGlobals() -> None:
    """
    Return list of globals inline eudplib code can call.
    """

    global _inlineGlobals

    # Add eudplib functions
    G = {}
    modules = [c, cs, sf, ut, t]
    for module in modules:
        for k, v in module.__dict__.items():
            if isinstance(v, types.ModuleType):
                continue
            if k[0] == "_":
                continue

            G[k] = v

    _inlineGlobals = G


def GetInlineCodeGlobals() -> dict[str, Any]:
    """
    Return list of globals inline eudplib code can call.
    """

    G = _inlineGlobals.copy()

    # Add custom registered functions
    for k, v in c.GetEUDNamespace().items():
        G[k] = v

    return G


def CompileInlineCode(code: str) -> tStartEnd:
    _code = compile(code, "<string>", "exec")

    if c.PushTriggerScope():
        tStart = RawTrigger(actions=c.SetDeaths(0, c.SetTo, 0, 0))
        exec(_code, GetInlineCodeGlobals(), {})
        tEnd = RawTrigger()
    c.PopTriggerScope()

    return tStart, tEnd
