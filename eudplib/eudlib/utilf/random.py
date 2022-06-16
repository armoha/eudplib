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
from ..memiof import f_wread_epd

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
    n = c.EUDLightVariable()
    c.RawTrigger(
        actions=[
            _seed.SetNumber(0),
            _seed.QueueAddTo(_seed),
            c.SetMemoryX(end + 328 + 24, c.SetTo, 5 << 24, 0xFF << 24),
            n.SetNumber(32),
        ]
    )
    c.RawTrigger(
        conditions=c.Switch("Switch 1", c.Set),
        actions=c.SetMemoryX(end + 328 + 24, c.SetTo, 4 << 24, 0xFF << 24),
    )

    if cs.EUDWhile()(n >= 1):
        # _seed += _seed
        c.VProc(
            _seed,
            [
                c.SetSwitch("Switch 1", c.Random),
                n.SubtractNumber(1),
            ],
        )
        c.RawTrigger(
            conditions=c.Switch("Switch 1", c.Set),
            actions=_seed.AddNumber(1),
        )
    cs.EUDEndWhile()

    end << c.RawTrigger(actions=c.SetSwitch("Switch 1", c.Set))


@c.EUDFunc
def f_rand():
    global _seed
    c.f_mul(_seed, 1103515245, ret=[_seed])
    _seed += 12345
    # Only HIWORD is returned
    return f_wread_epd(ut.EPD(_seed.getValueAddr()), 2)


@c.EUDFunc
def f_dwrand():
    dseed = c.f_mul(_seed, 1103515245)
    dseed += 12345
    c.f_mul(dseed, 1103515245, ret=[_seed])
    c.RawTrigger(
        actions=[
            _seed.AddNumber(12345),
            # HIWORD
            dseed.SetNumberX(0, 0xFFFF),
        ],
    )

    # LOWORD
    for i in ut.RandList(range(16, 32)):
        c.RawTrigger(
            conditions=_seed.AtLeastX(1, 2**i), actions=dseed.AddNumber(2 ** (i - 16))
        )

    return dseed
