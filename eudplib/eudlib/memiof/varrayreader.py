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

from eudplib import core as c, utils as ut


class EUDVArrayReader:
    def __init__(self):
        self._trg = c.Forward()
        self._fin = c.Forward()

    def _maketrg(self):
        c.PushTriggerScope()
        self._trg << c.RawTrigger(
            nextptr=0,
            actions=[c.SetDeaths(0, c.SetTo, 0, 0), c.SetNextPtr(0, self._fin)],
        )
        self._fin << c.RawTrigger(
            nextptr=0,
            actions=[
                c.SetMemory(self._trg + 4, c.Add, 72),
                c.SetMemory(self._trg + 328 + 16, c.Add, 18),
                c.SetMemory(self._trg + 360 + 16, c.Add, 18),
            ],
        )
        c.PopTriggerScope()

    def seek(self, varr_ptr, varr_epd, eudv, acts=[]):
        if not self._trg.IsSet():
            self._maketrg()

        if c.IsEUDVariable(varr_ptr):
            c.VProc(
                [varr_ptr, varr_epd],
                [
                    varr_ptr.QueueAssignTo(ut.EPD(self._trg) + 1),
                    varr_epd.AddNumber(1),
                    varr_epd.QueueAssignTo(ut.EPD(self._trg) + 360 // 4 + 4),
                    c.SetMemory(
                        self._trg + 328 + 20, c.SetTo, ut.EPD(eudv.getValueAddr())
                    ),
                ],
            )
            trg = c.VProc(
                varr_epd,
                [acts] + [varr_epd.AddNumber(328 // 4 + 3), varr_epd.AddDest(-8)],
            )
            return trg
        else:
            return [
                c.SetNextPtr(self._trg, varr_ptr),
                c.SetMemory(self._trg + 328 + 16, c.SetTo, varr_epd + 328 // 4 + 4),
                c.SetMemory(self._trg + 328 + 20, c.SetTo, ut.EPD(eudv.getValueAddr())),
                c.SetMemory(self._trg + 360 + 16, c.SetTo, varr_epd + 1),
            ]

    def read(self, acts=[]):
        if not self._trg.IsSet():
            self._maketrg()
        nptr = c.Forward()
        trg = c.RawTrigger(
            nextptr=self._trg, actions=[acts] + [c.SetNextPtr(self._fin, nptr)]
        )
        nptr << c.NextTrigger()
        return trg
