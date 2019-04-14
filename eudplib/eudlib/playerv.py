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
    def get(self, i):
        vtproc, _next = c.Forward(), c.Forward()
        ret = c.EUDVariable()
        a0, a1, a2 = c.Forward(), c.Forward(), c.Forward()
        c.RawTrigger(
            actions=[
                c.SetNextPtr(vtproc, self),
                c.SetMemory(a0 + 16, c.SetTo, self._epd + 344 // 4),
                c.SetMemory(a1 + 16, c.SetTo, self._epd + 352 // 4),
                c.SetMemory(a2 + 16, c.SetTo, self._epd + 1),
            ]
        )
        for k in range(2, -1, -1):
            c.RawTrigger(
                conditions=i.AtLeastX(1, 2 ** k),
                actions=[
                    c.SetMemory(vtproc + 4, c.Add, 72 * (2 ** k)),
                    c.SetMemory(a0 + 16, c.Add, 18 * (2 ** k)),
                    c.SetMemory(a1 + 16, c.Add, 18 * (2 ** k)),
                    c.SetMemory(a2 + 16, c.Add, 18 * (2 ** k)),
                ],
            )
        vtproc << c.RawTrigger(
            nextptr=self,
            actions=[
                a0 << c.SetMemory(0, c.SetTo, ut.EPD(ret.getValueAddr())),
                a1 << c.SetMemory(0, c.SetTo, 0x072D0000),
                a2 << c.SetNextPtr(self, _next),
            ],
        )
        _next << c.NextTrigger()
        return ret

    def set(self, i, value):
        _next = c.Forward()
        c.RawTrigger(
            actions=[
                value.QueueAssignTo(self._epd + 348 // 4),
                c.SetNextPtr(value.GetVTable(), _next),
            ]
        )
        for k in range(2, 0, -1):
            c.RawTrigger(
                conditions=i.AtLeastX(1, 2 ** k),
                actions=[c.SetMemory(value._varact + 16, c.Add, 18 * (2 ** k))],
            )
        c.RawTrigger(
            nextptr=value.GetVTable(),
            conditions=i.AtLeastX(1, 1),
            actions=[c.SetMemory(value._varact + 16, c.Add, 18)],
        )
        _next << c.NextTrigger()

    def __getitem__(self, i):
        if ut.isUnproxyInstance(i, c.EUDVariable):
            return self.get(i)
        else:
            return _EUDVariableFrom(_from=self + 72 * i)

    def __setitem__(self, i, value):
        if ut.isUnproxyInstance(i, c.EUDVariable) and ut.isUnproxyInstance(value, c.EUDVariable):
            self.set(i, value)

        elif ut.isUnproxyInstance(i, c.EUDVariable):
            a0 = c.Forward()
            c.RawTrigger(actions=[c.SetMemory(a0 + 16, c.SetTo, self._epd + 348 // 4)])
            for k in range(2, -1, -1):
                c.RawTrigger(
                    conditions=i.AtLeastX(1, 2 ** k),
                    actions=[c.SetMemory(a0 + 16, c.Add, 18 * (2 ** k))],
                )
            c.RawTrigger(actions=[a0 << c.SetMemory(0, c.SetTo, value)])

        elif ut.isUnproxyInstance(value, c.EUDVariable):
            c.VProc(value, value.QueueAssignTo(self._epd + (18 * i + 348 // 4)))

        else:
            c.RawTrigger(
                actions=[
                    c.SetDeaths(self._epd + (18 * i + 348 // 4), c.SetTo, value, 0)
                ]
            )

    """
    def __iter__(self):
        vtproc, _yield = c.Forward(), c.Forward()
        a0, a1, a2 = c.Forward(), c.Forward(), c.Forward()
        p, ret = c.EUDVariable(), c.EUDVariable()
        cs.DoActions([
            p.SetNumber(0),
            c.SetNextPtr(vtproc, self),
            c.SetMemory(a0 + 16, c.SetTo, self._epd + 344 // 4),
            c.SetMemory(a1 + 16, c.SetTo, self._epd + 352 // 4),
            c.SetMemory(a2 + 16, c.SetTo, self._epd + 1),
        ])
        if cs.EUDWhile()(p.AtMost(7)):
            cs.EUDContinueIfNot(f_playerexist(p))
            vtproc << c.RawTrigger(
                nextptr=self,
                actions=[
                    a0 << c.SetMemory(0, c.SetTo, ut.EPD(ret.getValueAddr())),
                    a1 << c.SetMemory(0, c.SetTo, 0x072D0000),
                    a2 << c.SetNextPtr(0, _yield),
                ]
            )
            _yield << c.NextTrigger()
            yield ret
            cs.EUDSetContinuePoint()
            cs.DoActions([
                p.AddNumber(1),
                c.SetMemory(vtproc + 4, c.Add, 72),
                c.SetMemory(a0 + 16, c.Add, 18),
                c.SetMemory(a1 + 16, c.Add, 18),
                c.SetMemory(a2 + 16, c.Add, 18),
            ])
        cs.EUDEndWhile()
    """
