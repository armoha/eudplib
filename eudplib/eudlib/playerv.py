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

from typing import Any

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from .utilf import f_playerexist


class _EUDVariableFrom(c.EUDVariable):
    def __init__(self, _from=None):
        self._vartrigger = _from
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False


_EUDVArray8: Any = c.EUDVArray(8)  # FIXME : Unsupported dynamic base class


class PVariable(_EUDVArray8):
    def _casteudset(self, i, value):
        nptr = c.Forward()
        c.VProc(
            self._epd,
            [
                value.SetDest(348 // 4),
                self._epd.QueueAddTo(ut.EPD(value.getDestAddr())),
                c.SetMemory(value._varact + 24, c.SetTo, 0x072D0000),
                c.SetNextPtr(value.GetVTable(), nptr),
            ],
        )
        for k in range(3):
            c.RawTrigger(conditions=i.AtLeastX(1, 2**k), actions=value.AddDest(18 * (2**k)))
        c.SetNextTrigger(value.GetVTable())
        nptr << c.NextTrigger()

    def _pveudset(self, i, value):
        nptr = c.Forward()
        cs.DoActions(
            value.SetDest(self._epd + 348 // 4),
            c.SetMemory(value._varact + 24, c.SetTo, 0x072D0000),
            c.SetNextPtr(value.GetVTable(), nptr),
        )
        for k in range(3):
            c.RawTrigger(conditions=i.AtLeastX(1, 2**k), actions=value.AddDest(18 * (2**k)))
        c.SetNextTrigger(value.GetVTable())
        nptr << c.NextTrigger()

    def __setitem__(self, i, value):
        i = c.EncodePlayer(i)
        if not c.IsEUDVariable(i):
            return self.set(i, value)
        if c.IsConstExpr(self):
            if c.IsEUDVariable(value):
                self._pveudset(i, value)
            else:
                a0 = c.Forward()
                cs.DoActions(c.SetMemory(a0 + 16, c.SetTo, self._epd + 348 // 4))
                for k in range(2, -1, -1):
                    c.RawTrigger(
                        conditions=i.AtLeastX(1, 2**k),
                        actions=c.SetMemory(a0 + 16, c.Add, 18 * (2**k)),
                    )
                c.RawTrigger(actions=[a0 << c.SetDeaths(0, c.SetTo, value, 0)])
        elif c.IsEUDVariable(value):
            self._casteudset(i, value)
        else:
            a0 = c.Forward()
            c.VProc(
                self._epd,
                [
                    c.SetMemory(a0 + 16, c.SetTo, 348 // 4),
                    self._epd.QueueAddTo(ut.EPD(a0 + 16)),
                ],
            )
            for k in range(3):
                c.RawTrigger(
                    conditions=i.AtLeastX(1, 2**k),
                    actions=c.SetMemory(a0 + 16, c.Add, 18 * (2**k)),
                )
            c.RawTrigger(actions=[a0 << c.SetDeaths(0, c.SetTo, value, 0)])

    def __getitem__(self, i):
        i = c.EncodePlayer(i)
        return super().__getitem__(i)
