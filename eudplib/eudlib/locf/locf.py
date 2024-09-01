#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import Literal, overload

from ... import core as c
from ... import utils as ut
from ...core.eudfunc.eudf import _EUDPredefineParam
from ...localize import _
from ...memio import f_dwread_cp, f_posread_cp, f_setcurpl2cpcache
from ...memio import modcurpl as cp

_loct = ut.EPD(0x58DC60) - 5


def _locfgen2(mod1, mod2, mod3, mod4, signed=False):
    @c.EUDFunc
    def _locf(epd, x, y):
        act = c.Forward()

        c.VProc(
            [epd, x],
            [
                epd.AddNumber(_loct),
                epd.SetDest(ut.EPD(act) + 4),
                x.SetDest(ut.EPD(act) + 5)
                if not signed
                else [
                    c.SetMemory(act + 20, c.SetTo, ~0),
                    x.QueueSubtractTo(ut.EPD(act) + 5),
                ],
            ],
        )
        settb = c.Forward()
        c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                c.SetMemory(act + 20, c.Add, 1) if signed else [],
                epd.AddNumber(2),
                epd.AddDest(16),
                x.AddDest(16),
                c.SetNextPtr(x.GetVTable(), settb),
                c.SetMemory(x._varact + 24, c.Subtract, 0x02000000)
                if signed
                else [],
            ],
        )
        settb << c.NextTrigger()
        c.VProc(
            [epd, y],
            [
                epd.AddNumber(-1),
                epd.AddDest(-8),
                y.SetDest(ut.EPD(act) + 8 + 5)
                if not signed
                else [
                    c.SetMemory(act + 52, c.SetTo, ~0),
                    y.QueueSubtractTo(ut.EPD(act) + 8 + 5),
                ],
            ],
        )
        setcoords = c.Forward()
        c.RawTrigger(
            nextptr=epd.GetVTable(),
            actions=[
                c.SetMemory(act + 52, c.Add, 1) if signed else [],
                epd.AddNumber(2),
                epd.AddDest(16),
                y.AddDest(16),
                c.SetNextPtr(y.GetVTable(), setcoords),
                c.SetMemory(y._varact + 24, c.Subtract, 0x02000000)
                if signed
                else [],
            ],
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
    def _locf(epd, left, t, r, b):
        act = c.Forward()

        c.VProc(
            [epd, left],
            [
                epd.AddNumber(_loct),
                epd.SetDest(ut.EPD(act) + 4),
                left.SetDest(ut.EPD(act) + 5)
                if not signed
                else [
                    c.SetMemory(act + 20, c.SetTo, ~0),
                    left.QueueSubtractTo(ut.EPD(act) + 5),
                ],
            ],
        )
        c.VProc(
            [epd, t],
            [
                c.SetMemory(act + 20, c.Add, 1) if signed else [],
                epd.AddNumber(1),
                epd.AddDest(8),
                t.SetDest(ut.EPD(act) + 8 + 5)
                if not signed
                else [
                    c.SetMemory(act + 52, c.SetTo, ~0),
                    t.QueueSubtractTo(ut.EPD(act) + 8 + 5),
                ],
            ],
        )
        c.VProc(
            [epd, r],
            [
                c.SetMemory(act + 52, c.Add, 1) if signed else [],
                epd.AddNumber(1),
                epd.AddDest(8),
                r.SetDest(ut.EPD(act) + 16 + 5),
            ],
        )
        c.VProc(
            [epd, b],
            [
                epd.AddNumber(1),
                epd.AddDest(8),
                b.SetDest(ut.EPD(act) + 24 + 5),
            ],
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


@overload
def f_setloc(loc, *coords, action: Literal[True]) -> list[c.Action]:
    ...


@overload
def f_setloc(loc, *coords, action: Literal[False]) -> None:
    ...


def f_setloc(loc, *coords, action=False):
    ut.ep_assert(
        len(coords) == 2 or len(coords) == 4,
        _("number of coordinates should be 2 or 4."),
    )
    loc = c.EncodeLocation(loc)
    if action is True:
        ut.ep_assert(all(c.IsConstExpr(x) for x in coords) and c.IsConstExpr(loc))
    if c.IsConstExpr(loc):
        dst = _loct + 5 * loc
        if len(coords) == 2:
            left, t = coords
            r, b = coords
        else:
            left, t, r, b = coords
        if action is True:
            return [
                c.SetMemoryEPD(dst + i, c.SetTo, x)
                for i, x in enumerate((left, t, r, b))
            ]
        c.NonSeqCompute(
            [
                (dst, c.SetTo, left),
                (dst + 1, c.SetTo, t),
                (dst + 2, c.SetTo, r),
                (dst + 3, c.SetTo, b),
            ]
        )
    elif len(coords) == 2:
        _SetLoc2(loc * 5, *coords)
    else:
        _SetLoc4(loc * 5, *coords)


@overload
def f_addloc(loc, *coords, action: Literal[True]) -> list[c.Action]:
    ...


@overload
def f_addloc(loc, *coords, action: Literal[False]) -> None:
    ...


def f_addloc(loc, *coords, action=False):
    ut.ep_assert(
        len(coords) == 2 or len(coords) == 4,
        _("number of coordinates should be 2 or 4."),
    )
    loc = c.EncodeLocation(loc)
    if action is True:
        ut.ep_assert(all(c.IsConstExpr(x) for x in coords) and c.IsConstExpr(loc))
    if c.IsConstExpr(loc):
        dst = _loct + 5 * loc
        if len(coords) == 2:
            left, t = coords
            r, b = coords
        else:
            left, t, r, b = coords
        if action is True:
            return [
                c.SetMemoryEPD(dst + i, c.Add, x)
                for i, x in enumerate((left, t, r, b))
                if not (isinstance(x, int) and x == 0)
            ]
        c.NonSeqCompute(
            [
                (dst + i, c.Add, x)
                for i, x in enumerate((left, t, r, b))
                if not (isinstance(x, int) and x == 0)
            ]
        )
    elif len(coords) == 2:
        _AddLoc2(loc * 5, *coords)
    else:
        _AddLoc4(loc * 5, *coords)


@overload
def f_dilateloc(loc, *coords, action: Literal[True]) -> list[c.Action]:
    ...


@overload
def f_dilateloc(loc, *coords, action: Literal[False]) -> None:
    ...


def f_dilateloc(loc, *coords, action=False):
    ut.ep_assert(
        len(coords) == 2 or len(coords) == 4,
        _("number of coordinates should be 2 or 4."),
    )
    loc = c.EncodeLocation(loc)
    if action is True:
        ut.ep_assert(all(c.IsConstExpr(x) for x in coords) and c.IsConstExpr(loc))
    if c.IsConstExpr(loc):
        dst = _loct + 5 * loc
        if len(coords) == 2:
            left, t = coords
            r, b = coords
        else:
            left, t, r, b = coords
        if action is True:
            return [
                c.SetMemoryEPD(dst + i, c.Add, x)
                for i, x in enumerate((-left, -t, r, b))
                if not (isinstance(x, int) and x == 0)
            ]
        c.NonSeqCompute(
            [
                (dst + i, c.Add, x)
                for i, x in enumerate((-left, -t, r, b))
                if not (isinstance(x, int) and x == 0)
            ]
        )
    elif len(coords) == 2:
        _DilateLoc2(loc * 5, *coords)
    else:
        _DilateLoc4(loc * 5, *coords)


@c.EUDFunc
def _getloc_tl(epd):
    c.VProc(epd, [epd.AddNumber(_loct), epd.SetDest(ut.EPD(0x6509B0))])
    left = f_dwread_cp(0)
    c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
    f_dwread_cp(0, ret=[epd])
    f_setcurpl2cpcache()
    return left, epd


def f_getlocTL(loc, **kwargs) -> tuple[c.EUDVariable, c.EUDVariable]:  # noqa: N802
    """
    로케이션의 위(top), 왼쪽 (left) 좌표를 얻어냅니다.
    @param {[type]} loc 로케이션 번호. $L(로케이션 이름) 으로 얻을 수 있습니다.
    """
    loc = c.EncodeLocation(loc)
    return _getloc_tl(loc * 5, **kwargs)


_set_loc: c.Action = c.SetMemory(0x6509B0, c.SetTo, 0)
_setcp2loc: c.ConstExpr = ut.EPD(_set_loc) + 5


@_EUDPredefineParam((_setcp2loc,), cp.CP)
@c.EUDFunc
def _setloc_epd(loc, epd):
    global _setcp2loc
    set_x_epd = c.Forward()
    f_posread_cp(0, ret=[set_x_epd, set_x_epd + 16])

    c.RawTrigger(
        actions=[
            _set_loc,
            c.SetMemory(0x6509B0, c.Add, _loct),
        ]
    )

    set_x = c.SetDeaths(cp.CP, c.SetTo, 0, 0)
    set_xy = c.RawTrigger(
        actions=[
            set_x,
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetDeaths(cp.CP, c.SetTo, 0, 0),
        ]
    )
    set_x_epd << ut.EPD(set_x) + 5

    done = c.Forward()
    one_more = c.RawTrigger(
        nextptr=set_xy,
        actions=[
            c.SetMemory(0x6509B0, c.Add, 1),
            c.SetNextPtr(set_xy, done),
        ],
    )
    done << f_setcurpl2cpcache(actions=c.SetNextPtr(set_xy, one_more))


def f_setloc_epd(loc, epd) -> None:
    if isinstance(loc, str):
        loc = c.GetLocationIndex(loc)
    _setloc_epd(loc * 5, epd)
