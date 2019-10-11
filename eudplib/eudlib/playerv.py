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

from .. import core as c, ctrlstru as cs, utils as ut
from .utilf import f_playerexist


class _EUDVariableFrom(c.EUDVariable):
    def __init__(self, _from=None):
        self._vartrigger = _from
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False


class PVariable(c.EUDVArray(8)):
    def _eudset(self, i, value):
        nptr = c.Forward()
        cs.DoActions(
            [
                value.SetDest(self._epd + 348 // 4),
                c.SetMemory(value._varact + 24, c.SetTo, 0x072D0000),
                c.SetNextPtr(value.GetVTable(), nptr),
            ]
        )
        for k in range(2, 0, -1):
            c.RawTrigger(
                conditions=i.AtLeastX(1, 2 ** k), actions=[value.AddDest(18 * (2 ** k))]
            )
        c.RawTrigger(
            nextptr=value.GetVTable(),
            conditions=i.AtLeastX(1, 1),
            actions=[value.AddDest(18)],
        )
        nptr << c.NextTrigger()

    def __setitem__(self, i, value):
        if ut.isUnproxyInstance(i, c.EUDVariable) and ut.isUnproxyInstance(
            value, c.EUDVariable
        ):
            self._eudset(i, value)

        elif ut.isUnproxyInstance(i, c.EUDVariable):
            a0 = c.Forward()
            cs.DoActions(c.SetMemory(a0 + 16, c.SetTo, self._epd + 348 // 4))
            for k in range(2, -1, -1):
                c.RawTrigger(
                    conditions=i.AtLeastX(1, 2 ** k),
                    actions=[c.SetMemory(a0 + 16, c.Add, 18 * (2 ** k))],
                )
            c.RawTrigger(actions=[a0 << c.SetMemory(0, c.SetTo, value)])

        else:
            self.set(i, value)
