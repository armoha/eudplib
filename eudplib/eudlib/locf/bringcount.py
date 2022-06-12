#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Armoha

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

from ... import core as c, ctrlstru as cs, utils as ut
from ...core.eudfunc.eudf import _EUDPredefineParam


bring = c.Bring(0, c.AtLeast, 0, 0, 0)


@_EUDPredefineParam((ut.EPD(bring) + 1, ut.EPD(bring) + 3, ut.EPD(bring)))
@c.EUDTypedFunc([c.TrgPlayer, c.TrgUnit, c.TrgLocation], [None])
def _bringcount(player, unit, location):
    cs.DoActions(
        c.SetMemory(bring + 8, c.SetTo, 1024),
        c.SetMemoryX(bring + 12, c.SetTo, 3 << 24, 0xFFFF0000),
    )
    c.RawTrigger(conditions=[bring, c.Memory(bring + 8, c.AtMost, 1700)])


def f_bringcount(player, unit, location):
    if not any(IsEUDVariable(v) for v in (player, unit, location)):
        cache = c.EUDVariable()
        cache_bring = c.Bring(player, c.Exactly, 0, unit, location)
        if cs.EUDIfNot()(cache_bring):
            _bringcount(player, unit, location, _ret=[cache])
            c.VProc(cache, cache.QueueAssignTo(ut.EPD(cache_bring) + 2))
        cs.EUDEndIf()
        return cache
    return _bringcount(player, unit, location)
