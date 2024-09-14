# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


import random
from typing import Any

from ..core.rawtrigger import (
    Action,
    Add,
    EncodeModifier,
    SetDeaths,
)
from ..utils import EPD
from . import modcurpl as cp

_seed = 0
_stack = []


def push() -> None:
    _stack.append(_seed)


def pop() -> None:
    _stack.pop()


def load() -> None:
    global _seed
    _seed = _stack[-1]


def rand(dest) -> tuple[Any, Any]:
    unit = random.randint(234, 65535)
    cpo = EPD(dest) - 12 * unit - _seed
    return cpo, unit


def srand() -> Action:
    r = random.randint(27, 0xFFFFFFFF)
    _loc = random.randint(1, 0xFFFFFFFF)
    u = random.randint(234, 65535)
    epd = EPD(0x6509B0) - 12 * u
    global _seed
    _seed = r
    return Action(_loc, 0, 0, 0, epd, r, u, 45, 7, 20)


def SetMemoryS(dest, modtype, value) -> tuple[Action, Action]:  # noqa: N802
    modtype = EncodeModifier(modtype)
    cpo, unit = rand(dest)
    return (
        SetMemoryC(0x6509B0, Add, cpo),
        SetDeaths(cp.CP, modtype, value, unit),
    )


def MoveCP(dest) -> Action:  # noqa: N802
    try:
        value = dest - _seed
    except (TypeError, AttributeError):
        value = _seed * (-1) + dest
    return SetMemoryC(0x6509B0, Add, value)


def SetMemoryC(dest, modtype, value) -> Action:  # noqa: N802
    modtype = EncodeModifier(modtype)
    _loc = random.randint(0, 0xFFFFFFFF)
    u = random.randint(234, 65535)
    epd = EPD(dest) - 12 * u
    if dest == 0x6509B0:
        global _seed
        if modtype == 7:
            _seed = value
        elif modtype == 9:
            try:
                _seed = _seed - value
            except (TypeError, AttributeError):
                _seed = -value + _seed
        else:
            try:
                _seed = _seed + value
            except (TypeError, AttributeError):
                _seed = value + _seed
    flag = random.randint(0, 0xFF) & (0xFF - 2)
    return Action(_loc, 0, 0, 0, epd, value, u, 45, modtype, flag)
