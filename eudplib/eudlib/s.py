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

from ..core.rawtrigger import (
    EncodeModifier,
    SetDeaths,
    Action,
    SetTo,
    Add,
    Subtract,
    CurrentPlayer,
)
from ..utils import EPD

_seed = 0
_stack = []


def push():
    _stack.append(_seed)


def pop():
    _stack.pop()


def load():
    global _seed
    _seed = _stack[-1]


def rand(dest):
    unit = random.randint(233, 65535)
    cpo = EPD(dest) - 12 * unit - _seed
    cpmod = Add
    if isinstance(cpo, int) and cpo < 0 and random.random() < 0.6:
        cpo = -cpo
        cpmod = Subtract
    return cpmod, cpo, unit


def srand():
    r = random.randint(27, 0xFFFFFFFF)
    _loc = random.randint(0, 0xFFFFFFFF)
    u = random.randint(233, 65535)
    epd = EPD(0x6509B0) - 12 * u
    flag = random.randint(0, 0xFF) & (0xFF - 2)
    global _seed
    _seed = r
    return Action(_loc, 0, 0, 0, epd, r, u, 45, 7, flag)


def SetMemoryS(dest, modtype, value):
    modtype = EncodeModifier(modtype, issueError=True)
    cpmod, cpo, unit = rand(dest)
    return [
        SetMemoryC(0x6509B0, cpmod, cpo),
        SetDeaths(CurrentPlayer, modtype, value, unit),
    ]


def MoveCP(dest):
    try:
        value = dest - _seed
    except TypeError:
        value = _seed * (-1) + dest
    return SetMemoryC(0x6509B0, Add, value)


def SetMemoryC(dest, modtype, value):
    modtype = EncodeModifier(modtype, issueError=True)
    _loc = random.randint(0, 0xFFFFFFFF)
    u = random.randint(233, 65535)
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
