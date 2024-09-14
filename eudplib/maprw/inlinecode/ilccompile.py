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
from .btinliner import t_start_end

_inline_globals = {}


def compute_base_inline_code_globals() -> None:
    """
    Return list of globals inline eudplib code can call.
    """

    global _inline_globals

    # Add eudplib functions
    g = {}
    modules = [c, cs, sf, ut, t]
    for module in modules:
        for k, v in module.__dict__.items():
            if isinstance(v, types.ModuleType):
                continue
            if k[0] == "_":
                continue

            g[k] = v

    _inline_globals = g


def get_inline_code_globals() -> dict[str, Any]:
    """
    Return list of globals inline eudplib code can call.
    """

    g = _inline_globals.copy()

    # Add custom registered functions
    for k, v in c.GetEUDNamespace().items():
        g[k] = v

    return g


def _compile_inline_code(code: str) -> t_start_end:
    _code = compile(code, "<string>", "exec")

    if c.PushTriggerScope():
        tstart = RawTrigger(actions=c.SetDeaths(0, c.SetTo, 0, 0))
        exec(_code, get_inline_code_globals(), {})
        tend = RawTrigger()
    c.PopTriggerScope()

    return tstart, tend
