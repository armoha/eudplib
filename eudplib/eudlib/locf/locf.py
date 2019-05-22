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

from ... import core as c, ctrlstru as cs, utils as ut
from ..memiof import f_posread_epd, f_getcurpl, f_dwread_epd


def _locfgen(mod1, mod2, mod3, mod4, signed=False):

    @c.EUDFunc
    def _locf(epd, x, y):
        L, T, R, B, fin, act = [c.Forward() for _ in range(6)]

        L << c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                epd.AddNumber(ut.EPD(0x58DC60)),
                epd.QueueAssignTo(ut.EPD(act) + 4),
                c.SetNextPtr(epd.GetVTable(), x.GetVTable()),
                [
                    x.QueueAssignTo(ut.EPD(act) + 5)
                    if not signed else [
                        c.SetMemory(act + 20, c.SetTo, ~0),
                        x.QueueSubtractTo(ut.EPD(act) + 5),
                    ]
                ],
                c.SetNextPtr(x.GetVTable(), T),
            ]
        )
        T << c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                [c.SetMemory(act + 20, c.Add, 1) if signed else []],
                epd.AddNumber(1),
                epd.AddDest(8),
                c.SetNextPtr(epd.GetVTable(), y.GetVTable()),
                [
                    y.QueueAssignTo(ut.EPD(act) + 8 + 5)
                    if not signed else [
                        c.SetMemory(act + 52, c.SetTo, ~0),
                        y.QueueSubtractTo(ut.EPD(act) + 8 + 5),
                    ]
                ],
                c.SetNextPtr(y.GetVTable(), R),
            ]
        )
        R << c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                [c.SetMemory(act + 52, c.Add, 1) if signed else []],
                epd.AddNumber(1),
                epd.AddDest(8),
                c.SetNextPtr(epd.GetVTable(), x.GetVTable()),
                x.AddDest(16),
                [
                    c.SetMemory(x._varact + 24, c.Subtract, 0x02000000)
                    if signed else []
                ],
                c.SetNextPtr(x.GetVTable(), B),
            ]
        )
        B << c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                epd.AddNumber(1),
                epd.AddDest(8),
                c.SetNextPtr(epd.GetVTable(), y.GetVTable()),
                y.AddDest(16),
                [
                    c.SetMemory(y._varact + 24, c.Subtract, 0x02000000)
                    if signed else []
                ],
                c.SetNextPtr(y.GetVTable(), fin),
            ]
        )
        fin << c.RawTrigger(
            actions=[
                act << c.SetMemory(0, mod1, 0),
                c.SetMemory(0, mod2, 0),
                c.SetMemory(0, mod3, 0),
                c.SetMemory(0, mod4, 0),
            ]
        )

    return _locf


_SetLoc = _locfgen(c.SetTo, c.SetTo, c.SetTo, c.SetTo)
_AddLoc = _locfgen(c.Add, c.Add, c.Add, c.Add)
_DilateLoc = _locfgen(c.Add, c.Add, c.Add, c.Add, signed=True)


def f_setloc(locID, x, y):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    _SetLoc(locID * 5, x, y)


def f_addloc(locID, x, y):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    _AddLoc(locID * 5, x, y)


def f_dilateloc(locID, x, y):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    _DilateLoc(locID * 5, x, y)


@c.EUDFunc
def _GetLocTL(epd):
    epd += ut.EPD(0x58DC60)
    c.EUDReturn(
        f_dwread_epd(epd),
        f_dwread_epd(epd + 1))


def f_getlocTL(locID):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    # 로케이션의 위(top), 왼쪽 (left) 좌표를 얻어냅니다.
    # @param  {[type]} locID 로케이션 번호. $L(로케이션 이름) 으로 얻을 수 있습니다.
    return _GetLocTL(locID * 5)


@c.EUDFunc
def _SetLocEPD(loc, epd):
    origcp = f_getcurpl()
    x, y = f_posread_epd(epd)

    act, t1, t2 = c.Forward(), c.Forward(), c.Forward()

    c.RawTrigger(
        nextptr=loc.GetVTable(),
        actions=[
            loc.QueueAssignTo(ut.EPD(act) + 5),
            c.SetNextPtr(loc.GetVTable(), x.GetVTable()),
            x.QueueAssignTo(ut.EPD(act) + 5 + 8 * 2),
            c.SetNextPtr(x.GetVTable(), y.GetVTable()),
            y.QueueAssignTo(ut.EPD(act) + 5 + 8 * 4),
            c.SetNextPtr(y.GetVTable(), t1),
        ]
    )

    t1 << c.RawTrigger(
        nextptr=x.GetVTable(),
        actions=[
            x.QueueAssignTo(ut.EPD(act) + 5 + 8 * 6),
            c.SetNextPtr(x.GetVTable(), y.GetVTable()),
            y.QueueAssignTo(ut.EPD(act) + 5 + 8 * 8),
            c.SetNextPtr(y.GetVTable(), origcp.GetVTable()),
            origcp.QueueAssignTo(ut.EPD(act) + 5 + 8 * 9),
            c.SetNextPtr(origcp.GetVTable(), t2),
        ]
    )

    t2 << c.RawTrigger(
        actions=[
            act << c.SetMemory(0x6509B0, c.SetTo, 0),
            c.SetMemory(0x6509B0, c.Add, ut.EPD(0x58DC60)),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.SetTo, 0),
        ]
    )


def f_setloc_epd(locID, epd):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    return _SetLocEPD(locID * 5, epd)
