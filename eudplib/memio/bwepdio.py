#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from . import cpmemio as cpm
from . import dwepdio as dwm
from . import iotable
from . import modcurpl as cp

# Helper functions


def _lshift(a, b):
    if c.IsEUDVariable(a):
        return c.f_bitlshift(a, b)
    if isinstance(b, int) and b == 0:
        return a
    return a << b


@c.EUDFunc
def _wwriter(epd, subp, w):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(3)):
        if cs.EUDSwitchCase()(i):
            c.f_bitlshift(w, 8 * i, ret=[w])
            cs.DoActions(c.SetDeathsX(cp.CP, c.SetTo, w, 0, 0xFFFF << (8 * i)))
            cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0, b1 = dwm.f_dwbreak(w)[2:4]
        cpm.f_bwrite_cp(0, 3, b0)
        cpm.f_bwrite_cp(1, 0, b1)

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()


def f_wwrite_epd(epd, subp, w):
    if isinstance(subp, int) and isinstance(w, int):
        if subp == 3:
            return _wwriter(epd, subp, w)
        cs.DoActions(
            c.SetDeathsX(epd, c.SetTo, _lshift(w, 8 * subp), 0, 0xFFFF << (8 * subp))
        )
    else:
        _wwriter(epd, subp, w)


@c.EUDFunc
def _wadder(epd, subp, w):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(3)):
        if cs.EUDSwitchCase()(i):
            c.f_bitlshift(w, 8 * i, ret=[w])
            cs.DoActions(c.SetDeathsX(cp.CP, c.Add, w, 0, 0xFFFF << (8 * i)))
            cs.EUDBreak()

    # Not implemented yet
    # if cs.EUDSwitchCase()(3):

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()


def f_wadd_epd(epd, subp, w):
    ut.ep_assert(isinstance(subp, int) and 0 <= subp <= 2)
    if isinstance(subp, int) and isinstance(w, int):
        if subp == 3:
            return _wadder(epd, subp, w)
        cs.DoActions(
            c.SetDeathsX(epd, c.Add, _lshift(w, 8 * subp), 0, 0xFFFF << (8 * subp))
        )
    else:
        _wadder(epd, subp, w)


@c.EUDFunc
def _wsubtracter(epd, subp, w):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(3)):
        if cs.EUDSwitchCase()(i):
            c.f_bitlshift(w, 8 * i, ret=[w])
            cs.DoActions(c.SetDeathsX(cp.CP, c.Subtract, w, 0, 0xFFFF << (8 * i)))
            cs.EUDBreak()

    # Not implemented yet
    # if cs.EUDSwitchCase()(3):

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()


def f_wsubtract_epd(epd, subp, w):
    ut.ep_assert(isinstance(subp, int) and 0 <= subp <= 2)
    if isinstance(subp, int) and isinstance(w, int):
        if subp == 3:
            return _wsubtracter(epd, subp, w)
        cs.DoActions(
            c.SetDeathsX(
                epd, c.Subtract, _lshift(w, 8 * subp), 0, 0xFFFF << (8 * subp)
            )
        )
    else:
        _wsubtracter(epd, subp, w)


@c.EUDFunc
def _bwriter(epd, subp, b):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            cs.DoActions(
                c.SetDeathsX(
                    cp.CP,
                    c.SetTo,
                    _lshift(b, 8 * i),
                    0,
                    0xFF << (8 * i),
                )
            )
            cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return b


def f_bwrite_epd(epd, subp, b):
    if isinstance(subp, int) and isinstance(b, int):
        cs.DoActions(
            c.SetDeathsX(epd, c.SetTo, _lshift(b, 8 * subp), 0, 0xFF << (8 * subp))
        )
    else:
        _bwriter(epd, subp, b)


@c.EUDFunc
def _badder(epd, subp, b):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            c.f_bitlshift(b, 8 * i, ret=[b])
            cs.DoActions(c.SetDeathsX(13, c.Add, b, 0, 0xFF << (8 * i)))
            cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return b


def f_badd_epd(epd, subp, b):
    if isinstance(subp, int) and isinstance(b, int):
        cs.DoActions(
            c.SetDeathsX(epd, c.Add, _lshift(b, 8 * subp), 0, 0xFF << (8 * subp))
        )
    else:
        _badder(epd, subp, b)


@c.EUDFunc
def _bsubtracter(epd, subp, b):
    c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            c.f_bitlshift(b, 8 * i, ret=[b])
            cs.DoActions(c.SetDeathsX(cp.CP, c.Subtract, b, 0, 0xFF << (8 * i)))
            cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return b


def f_bsubtract_epd(epd, subp, b):
    if isinstance(subp, int) and isinstance(b, int):
        cs.DoActions(
            c.SetDeathsX(
                epd, c.Subtract, _lshift(b, 8 * subp), 0, 0xFF << (8 * subp)
            )
        )
    else:
        _bsubtracter(epd, subp, b)


# -----------------------------


@c.EUDFunc
def _wread_epd(epd, subp):
    w = c.EUDVariable()
    c.VProc(epd, [epd.SetDest(ut.EPD(0x6509B0)), w.SetNumber(0)])
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(3)):
        if cs.EUDSwitchCase()(i):
            for j in ut._rand_lst(range(8 * i, 8 * i + 16)):
                c.RawTrigger(
                    conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**j),
                    actions=w.AddNumber(2 ** (j - 8 * i)),
                )

            cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0 = cpm.f_bread_cp(0, 3)
        b1 = cpm.f_bread_cp(1, 0)
        w << b0 + b1 * 256

    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return w


def f_wread_epd(epd, subp, *, ret=None):
    if isinstance(subp, int) and 0 <= subp <= 2:
        return iotable._insert_or_get(0xFFFF << (8 * subp), -(8 * subp))(
            epd, ret=ret
        )

    return _wread_epd(epd, subp, ret=ret)


@c.EUDFunc
def _bread_epd(epd, subp) -> c.EUDVariable:
    b = c.EUDVariable()
    c.VProc(epd, [epd.SetDest(ut.EPD(0x6509B0)), b.SetNumber(0)])
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            for j in ut._rand_lst(range(8 * i, 8 * i + 8)):
                c.RawTrigger(
                    conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**j),
                    actions=b.AddNumber(2 ** (j - 8 * i)),
                )

            cs.EUDBreak()
    cs.EUDEndSwitch()
    cp.f_setcurpl2cpcache()
    return b


def f_bread_epd(epd, subp, *, ret=None):
    if isinstance(subp, int) and 0 <= subp <= 3:
        return iotable._insert_or_get(0xFF << (8 * subp), -(8 * subp))(epd, ret=ret)

    return _bread_epd(epd, subp, ret=ret)


def f_maskwrite_epd(epd, value, mask) -> None:
    cs.DoActions(c.SetDeathsX(epd, c.SetTo, value, 0, mask))
