#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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


import random
from typing import Any

from ..core.rawtrigger import (
    Action,
    Add,
    Condition,
    CurrentPlayer,
    EncodeModifier,
    SetDeaths,
    SetTo,
    Subtract,
)
from ..utils import EPD

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


def SetMemoryS(dest, modtype, value) -> tuple[Action, Action]:
    modtype = EncodeModifier(modtype, issueError=True)
    cpo, unit = rand(dest)
    return (
        SetMemoryC(0x6509B0, Add, cpo),
        SetDeaths(CurrentPlayer, modtype, value, unit),
    )


def MoveCP(dest) -> Action:
    try:
        value = dest - _seed
    except TypeError:
        value = _seed * (-1) + dest
    return SetMemoryC(0x6509B0, Add, value)


def SetMemoryC(dest, modtype, value) -> Action:
    modtype = EncodeModifier(modtype, issueError=True)
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
            except TypeError:
                _seed = -value + _seed
        else:
            try:
                _seed = _seed + value
            except TypeError:
                _seed = value + _seed
    flag = random.randint(0, 0xFF) & (0xFF - 2)
    return Action(_loc, 0, 0, 0, epd, value, u, 45, modtype, flag)
