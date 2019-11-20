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
from ..memiof import f_posread_epd, f_setcurpl2cpcache, f_dwread_epd

_loct = ut.EPD(0x58DC60)


def _locfgen2(mod1, mod2, mod3, mod4, signed=False):
    @c.EUDFunc
    def _locf(epd, x, y):
        act = c.Forward()

        c.VProc(
            [epd, x],
            [epd.AddNumber(_loct), epd.SetDest(ut.EPD(act) + 4)]
            + [
                x.SetDest(ut.EPD(act) + 5)
                if not signed
                else [
                    c.SetMemory(act + 20, c.SetTo, ~0),
                    x.QueueSubtractTo(ut.EPD(act) + 5),
                ]
            ],
        )
        settb = c.Forward()
        c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                [c.SetMemory(act + 20, c.Add, 1) if signed else []],
                epd.AddNumber(2),
                epd.AddDest(16),
                x.AddDest(16),
                c.SetNextPtr(x.GetVTable(), settb),
            ]
            + [c.SetMemory(x._varact + 24, c.Subtract, 0x02000000) if signed else []],
        )
        settb << c.NextTrigger()
        c.VProc(
            [epd, y],
            [epd.AddNumber(-1), epd.AddDest(-8)]
            + [
                y.SetDest(ut.EPD(act) + 8 + 5)
                if not signed
                else [
                    c.SetMemory(act + 52, c.SetTo, ~0),
                    y.QueueSubtractTo(ut.EPD(act) + 8 + 5),
                ]
            ],
        )
        setcoords = c.Forward()
        c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                [c.SetMemory(act + 52, c.Add, 1) if signed else []],
                epd.AddNumber(2),
                epd.AddDest(16),
                y.AddDest(16),
                c.SetNextPtr(y.GetVTable(), setcoords),
            ]
            + [c.SetMemory(y._varact + 24, c.Subtract, 0x02000000) if signed else []],
        )
        setcoords << c.NextTrigger()
        c.RawTrigger(
            actions=[
                act << c.SetDeaths(0, mod1, 0, 0),
                c.SetDeaths(0, mod2, 0, 0),
                c.SetDeaths(0, mod3, 0, 0),
                c.SetDeaths(0, mod4, 0, 0),
            ]
        )

    return _locf


def _locfgen4(mod1, mod2, mod3, mod4, signed=False):
    @c.EUDFunc
    def _locf(epd, l, t, r, b):
        act = c.Forward()

        c.VProc(
            [epd, l],
            [epd.AddNumber(_loct), epd.SetDest(ut.EPD(act) + 4)]
            + [
                l.SetDest(ut.EPD(act) + 5)
                if not signed
                else [
                    c.SetMemory(act + 20, c.SetTo, ~0),
                    l.QueueSubtractTo(ut.EPD(act) + 5),
                ]
            ],
        )
        c.VProc(
            [epd, t],
            [
                [c.SetMemory(act + 20, c.Add, 1) if signed else []],
                epd.AddNumber(1),
                epd.AddDest(8),
            ]
            + [
                t.SetDest(ut.EPD(act) + 8 + 5)
                if not signed
                else [
                    c.SetMemory(act + 52, c.SetTo, ~0),
                    t.QueueSubtractTo(ut.EPD(act) + 8 + 5),
                ]
            ],
        )
        c.VProc(
            [epd, r],
            [
                [c.SetMemory(act + 52, c.Add, 1) if signed else []],
                epd.AddNumber(1),
                epd.AddDest(8),
                r.SetDest(ut.EPD(act) + 16 + 5),
            ],
        )
        c.VProc(
            [epd, b],
            [epd.AddNumber(1), epd.AddDest(8), b.SetDest(ut.EPD(act) + 24 + 5)],
        )
        c.RawTrigger(
            actions=[
                act << c.SetDeaths(0, mod1, 0, 0),
                c.SetDeaths(0, mod2, 0, 0),
                c.SetDeaths(0, mod3, 0, 0),
                c.SetDeaths(0, mod4, 0, 0),
            ]
        )

    return _locf


_SetLoc2 = _locfgen2(c.SetTo, c.SetTo, c.SetTo, c.SetTo)
_AddLoc2 = _locfgen2(c.Add, c.Add, c.Add, c.Add)
_DilateLoc2 = _locfgen2(c.Add, c.Add, c.Add, c.Add, signed=True)
_SetLoc4 = _locfgen4(c.SetTo, c.SetTo, c.SetTo, c.SetTo)
_AddLoc4 = _locfgen4(c.Add, c.Add, c.Add, c.Add)
_DilateLoc4 = _locfgen4(c.Add, c.Add, c.Add, c.Add, signed=True)


def f_setloc(locID, *coords):
    if len(coords) != 2 and len(coords) != 4:
        raise NotImplementedError("number of coordinates should be 2 or 4.")
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    if c.IsConstExpr(locID):
        dst = _loct + 5 * locID
        if len(coords) == 2:
            l, t = coords
            r, b = coords
        else:
            l, t, r, b = coords
        c.SeqCompute(
            [
                (dst, c.SetTo, l),
                (dst + 1, c.SetTo, t),
                (dst + 2, c.SetTo, r),
                (dst + 3, c.SetTo, b),
            ]
        )
    elif len(coords) == 2:
        _SetLoc2(locID * 5, *coords)
    else:
        _SetLoc4(locID * 5, *coords)


def f_addloc(locID, *coords):
    if len(coords) != 2 and len(coords) != 4:
        raise NotImplementedError("number of coordinates should be 2 or 4.")
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    if c.IsConstExpr(locID):
        dst = _loct + 5 * locID
        if len(coords) == 2:
            l, t = coords
            r, b = coords
        else:
            l, t, r, b = coords
        c.SeqCompute(
            [
                (dst, c.Add, l),
                (dst + 1, c.Add, t),
                (dst + 2, c.Add, r),
                (dst + 3, c.Add, b),
            ]
        )
    elif len(coords) == 2:
        _AddLoc2(locID * 5, *coords)
    else:
        _AddLoc4(locID * 5, *coords)


def f_dilateloc(locID, *coords):
    if len(coords) != 2 and len(coords) != 4:
        raise NotImplementedError("number of coordinates should be 2 or 4.")
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    if c.IsConstExpr(locID):
        dst = _loct + 5 * locID
        if len(coords) == 2:
            l, t = coords
            r, b = coords
        else:
            l, t, r, b = coords
        c.SeqCompute(
            [
                (dst, c.Add, -l),
                (dst + 1, c.Add, -t),
                (dst + 2, c.Add, r),
                (dst + 3, c.Add, b),
            ]
        )
    elif len(coords) == 2:
        _DilateLoc2(locID * 5, *coords)
    else:
        _DilateLoc4(locID * 5, *coords)


@c.EUDFunc
def _GetLocTL(epd):
    epd += _loct
    left = f_dwread_epd(epd)
    epd += 1
    f_dwread_epd(epd, ret=epd)
    return left, epd


def f_getlocTL(locID, **kwargs):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    # 로케이션의 위(top), 왼쪽 (left) 좌표를 얻어냅니다.
    # @param  {[type]} locID 로케이션 번호. $L(로케이션 이름) 으로 얻을 수 있습니다.
    return _GetLocTL(locID * 5, **kwargs)


@c.EUDFunc
def _SetLocEPD(loc, epd):
    x, y = f_posread_epd(epd)

    act, nptr = c.Forward(), c.Forward()

    c.VProc(
        [loc, x, y],
        [
            loc.SetDest(ut.EPD(0x6509B0)),
            x.SetDest(ut.EPD(act + 32 * 0 + 20)),
            y.SetDest(ut.EPD(act + 32 * 2 + 20)),
        ],
    )

    c.RawTrigger(
        nextptr=x.GetVTable(),
        actions=[
            c.SetMemory(0x6509B0, c.Add, _loct),
            x.SetDest(ut.EPD(act + 32 * 4 + 20)),
            y.SetDest(ut.EPD(act + 32 * 6 + 20)),
            c.SetNextPtr(y.GetVTable(), nptr),
        ],
    )
    nptr << c.NextTrigger()
    f_setcurpl2cpcache(
        actions=[
            act << c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
        ]
    )


def f_setloc_epd(locID, epd):
    if isinstance(locID, str):
        locID = c.GetLocationIndex(locID)
    return _SetLocEPD(locID * 5, epd)
