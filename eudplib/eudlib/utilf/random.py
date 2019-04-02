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

# This code uses simple LCG algorithm.

from eudplib import core as c, ctrlstru as cs
from ..memiof import f_dwbreak

_seed = c.EUDVariable()


def f_getseed():
    t = c.EUDVariable()
    t << _seed
    return t


def f_srand(seed):
    _seed << seed


def f_randomize():
    global _seed

    # Store switch 1
    sw1 = c.EUDVariable()
    if cs.EUDIf()(c.Switch("Switch 1", c.Set)):
        sw1 << c.EncodeSwitchAction(c.Set)
    if cs.EUDElse()():
        sw1 << c.EncodeSwitchAction(c.Clear)
    cs.EUDEndIf()

    _seed << 0
    dseed = c.EUDVariable()
    dseed << 1

    if cs.EUDLoopN()(32):
        cs.DoActions(c.SetSwitch("Switch 1", c.Random))
        if cs.EUDIf()(c.Switch("Switch 1", c.Set)):
            _seed += dseed
        cs.EUDEndIf()
        dseed += dseed
    cs.EUDEndLoopN()

    cs.DoActions(c.SetSwitch("Switch 1", sw1))


@c.EUDFunc
def f_rand():
    _seed << c.f_mul(_seed, 1103515245) + 12345
    return f_dwbreak(_seed)[1]  # Only HIWORD is returned


@c.EUDFunc
def f_dwrand():
    seed1 = c.f_mul(_seed, 1103515245) + 12345
    seed2 = c.f_mul(seed1, 1103515245) + 12345
    _seed << seed2

    ret = c.EUDVariable()
    ret << 0

    # HIWORD
    for i in range(31, 15, -1):
        c.RawTrigger(
            conditions=seed1.AtLeast(2 ** i),
            actions=[seed1.SubtractNumber(2 ** i), ret.AddNumber(2 ** i)],
        )

    # LOWORD
    for i in range(31, 15, -1):
        c.RawTrigger(
            conditions=seed2.AtLeast(2 ** i),
            actions=[seed2.SubtractNumber(2 ** i), ret.AddNumber(2 ** (i - 16))],
        )

    return ret
