# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from . import cpmemio as cpm
from . import dwepdio as dwm
from . import modcurpl as cp
from . import readtable

cpcache = c.curpl.GetCPCache()

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


def f_bwrite_epd(epd, subp, b) -> None:
    if isinstance(subp, int) and isinstance(b, int):
        cs.DoActions(
            c.SetDeathsX(epd, c.SetTo, _lshift(b, 8 * subp), 0, 0xFF << (8 * subp))
        )
    else:
        _bwriter(epd, subp, b)


def _bitwrite_epd(epd, subp, bit, b) -> None:
    ut.ep_assert(
        isinstance(bit, int) and bit.bit_count() == 1, f"bit_count is not 1: {bit}"
    )
    if isinstance(subp, int):
        bit <<= 8 * subp
        if c.IsEUDVariable(b):
            from ..trigger import Trigger

            cs.DoActions(c.SetDeathsX(epd, c.SetTo, 0, 0, bit))
            Trigger(
                conditions=b.AtLeast(1),
                actions=c.SetDeathsX(epd, c.SetTo, bit, 0, bit),
            )
        elif b == 0:
            cs.DoActions(c.SetDeathsX(epd, c.SetTo, 0, 0, bit))
        else:
            cs.DoActions(c.SetDeathsX(epd, c.SetTo, bit, 0, bit))
        return

    try:
        f = getattr(_bitwrite_epd, "f")
    except AttributeError:
        f = {}
        setattr(_bitwrite_epd, "f", f)

    try:
        _bitwriter = f[bit]
    except KeyError:

        @c.EUDFunc
        def _bitwriter(epd, subp, b):
            c.VProc(epd, epd.SetDest(ut.EPD(0x6509B0)))
            cs.EUDSwitch(subp)
            for i in ut._rand_lst(range(4)):
                if cs.EUDSwitchCase()(i):
                    c.RawTrigger(
                        actions=c.SetDeathsX(cp.CP, c.SetTo, 0, 0, bit << (8 * i))
                    )
                    c.RawTrigger(
                        conditions=b.AtLeast(1),
                        actions=c.SetDeathsX(
                            cp.CP, c.SetTo, bit << (8 * i), 0, bit << (8 * i)
                        ),
                    )
                    cs.EUDBreak()
            cs.EUDEndSwitch()
            cp.f_setcurpl2cpcache()
            return b

        f[bit] = _bitwriter

    return _bitwriter(epd, subp, b)


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


@_EUDPredefineReturn(1, 2)
@_EUDPredefineParam(cp.CP, 1)
@c.EUDFunc
def _wread_epd(epd, subp):
    w = _wread_epd._frets[0]
    fend = c.Forward()
    cs.EUDSwitch(subp)
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    block["_actions"].extend(
        [
            c.SetNextPtr(readtable.read_end_common, block["swend"]),
            c.SetMemory(readtable.copy_ret + 16, c.SetTo, ut.EPD(w.getValueAddr())),
            c.SetNextPtr(cpcache.GetVTable(), fend),
            cpcache.SetDest(ut.EPD(0x6509B0)),
        ]
    )
    for i in range(3):
        if cs.EUDSwitchCase()(i):
            readtrg = readtable._insert_or_get(0xFFFF << (8 * i), -(8 * i))
            c.SetNextTrigger(readtrg)

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        readtrg = readtable._insert_or_get(0xFF000000, -24)
        trg2, trg3 = c.Forward(), c.Forward()
        c.RawTrigger(
            nextptr=readtrg,
            actions=c.SetNextPtr(readtable.read_end_common, trg2),
        )
        readtrg = readtable._insert_or_get(0xFF, 8)
        trg2 << c.RawTrigger(
            nextptr=readtrg,
            actions=[
                c.SetMemory(0x6509B0, c.Add, 1),
                c.SetMemoryX(readtable.copy_ret + 24, c.SetTo, 8 << 24, 0xFF000000),
                c.SetNextPtr(readtable.read_end_common, trg3),
            ],
        )
        trg3 << c.RawTrigger(
            actions=c.SetMemoryX(
                readtable.copy_ret + 24, c.SetTo, 7 << 24, 0xFF000000
            )
        )

    cs.EUDEndSwitch()
    c.SetNextTrigger(cpcache.GetVTable())
    fend << c.NextTrigger()
    # return w


def f_wread_epd(epd, subp, *, ret=None):
    if isinstance(subp, int) and 0 <= subp <= 2:
        return readtable._epd_caller(
            readtable._insert_or_get(0xFFFF << (8 * subp), -(8 * subp))
        )(epd, ret=ret)

    return _wread_epd(epd, subp, ret=ret)


@_EUDPredefineReturn(1, 2)
@_EUDPredefineParam(cp.CP, 1)
@c.EUDFunc
def _bread_epd(epd, subp):
    b = _bread_epd._frets[0]
    fend = c.Forward()
    cs.EUDSwitch(subp)
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    block["_actions"].extend(
        [
            c.SetNextPtr(readtable.read_end_common, block["swend"]),
            c.SetMemory(readtable.copy_ret + 16, c.SetTo, ut.EPD(b.getValueAddr())),
            c.SetNextPtr(cpcache.GetVTable(), fend),
            cpcache.SetDest(ut.EPD(0x6509B0)),
        ]
    )
    for i in range(4):
        if cs.EUDSwitchCase()(i):
            readtrg = readtable._insert_or_get(0xFF << (8 * i), -(8 * i))
            c.SetNextTrigger(readtrg)
    cs.EUDEndSwitch()
    c.SetNextTrigger(cpcache.GetVTable())
    fend << c.NextTrigger()
    # return b


def f_bread_epd(epd, subp, *, ret=None):
    if isinstance(subp, int) and 0 <= subp <= 3:
        return readtable._epd_caller(
            readtable._insert_or_get(0xFF << (8 * subp), -(8 * subp))
        )(epd, ret=ret)

    return _bread_epd(epd, subp, ret=ret)


@_EUDPredefineReturn(1, 2)
@_EUDPredefineParam(cp.CP, 1)
@c.EUDFunc
def _boolread_epd(epd, subp):
    b = _boolread_epd._frets[0]
    fend = c.Forward()
    cs.EUDSwitch(subp)
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    block["_actions"].extend(
        [
            b.SetNumber(0),
            c.SetNextPtr(cpcache.GetVTable(), fend),
            cpcache.SetDest(ut.EPD(0x6509B0)),
        ]
    )
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 0xFF << (8 * i)),
                actions=b.SetNumber(1),
            )
            c.SetNextTrigger(cpcache.GetVTable())
    cs.EUDEndSwitch()
    fend << c.NextTrigger()
    # return b


def f_maskwrite_epd(epd, value, mask) -> None:
    cs.DoActions(c.SetDeathsX(epd, c.SetTo, value, 0, mask))


def _bitread_epd(bit):
    ut.ep_assert(
        isinstance(bit, int) and bit.bit_count() == 1, f"bit_count is not 1: {bit}"
    )
    f = getattr(_bitread_epd, "f", None)
    if f is None:
        f = {}
        _bitread_epd.f = f
    try:
        readfn = f[bit]
    except KeyError:

        @c.EUDFunc
        def readfn(epd, subp):
            b = c.EUDVariable()
            c.VProc(epd, [epd.SetDest(ut.EPD(0x6509B0)), b.SetNumber(0)])
            cs.EUDSwitch(subp)
            for i in ut._rand_lst(range(4)):
                if cs.EUDSwitchCase()(i):
                    mask = bit << (8 * i)
                    c.RawTrigger(
                        conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, mask),
                        actions=b.SetNumber(1),
                    )
                    cs.EUDBreak()
            cs.EUDEndSwitch()
            cp.f_setcurpl2cpcache()
            return b

        f[bit] = readfn

    return readfn
