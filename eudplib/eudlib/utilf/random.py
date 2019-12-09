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

from eudplib import core as c, ctrlstru as cs, utils as ut
from ..memiof import f_dwbreak

_seed = c.EUDVariable()


def f_getseed():
    t = c.EUDVariable()
    t << _seed
    return t


def f_srand(seed):
    _seed << seed


@c.EUDFunc
def f_randomize():
    global _seed

    # Store switch 1
    end = c.Forward()
    c.RawTrigger(
        conditions=c.Switch("Switch 1", c.Set),
        actions=c.SetMemoryX(end + 328 + 24, c.SetTo, 4 << 24, 0xFF << 24),
    )
    c.RawTrigger(
        conditions=c.Switch("Switch 1", c.Cleared),
        actions=c.SetMemoryX(end + 328 + 24, c.SetTo, 5 << 24, 0xFF << 24),
    )

    dseed = c.EUDVariable()
    n = c.EUDLightVariable()
    c.RawTrigger(
        actions=[
            _seed.SetNumber(0),
            dseed.SetNumber(1),
            c.SetSwitch("Switch 1", c.Random),
            n.SetNumber(32),
        ]
    )

    if cs.EUDWhile()(n >= 1):
        if cs.EUDIf()(c.Switch("Switch 1", c.Set)):
            _seed += dseed
        cs.EUDEndIf()
        c.VProc(
            dseed,
            [
                dseed.QueueAddTo(dseed),
                c.SetSwitch("Switch 1", c.Random),
                n.SubtractNumber(1),
            ],
        )
    cs.EUDEndWhile()

    end << c.RawTrigger(actions=c.SetSwitch("Switch 1", c.Set))


@c.EUDFunc
def f_rand():
    seed = c.f_mul(_seed, 1103515245)
    c.VProc(seed, [seed.AddNumber(12345), seed.SetDest(_seed)])
    return f_dwbreak(_seed)[1]  # Only HIWORD is returned


@c.EUDFunc
def f_dwrand():
    seed1 = c.f_mul(_seed, 1103515245)
    seed1 += 12345
    seed2 = c.f_mul(seed1, 1103515245)
    c.VProc(
        seed2,
        [
            seed2.AddNumber(12345),
            seed2.SetDest(_seed),
            # HIWORD
            seed1.SetNumberX(0, 0xFFFF),
        ],
    )

    # LOWORD
    for i in ut.RandList(range(16, 32)):
        c.RawTrigger(
            conditions=seed2.AtLeastX(1, 2 ** i), actions=seed1.AddNumber(2 ** (i - 16))
        )

    return seed1
