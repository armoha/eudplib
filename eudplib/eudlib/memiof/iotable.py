#!/usr/bin/python
# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from collections.abc import Callable

from ... import core as c
from ... import utils as ut
from . import modcurpl

_table = {}

c.PushTriggerScope()
_writeact = c.SetDeaths(0, c.SetTo, 0, 0)
_readend = modcurpl.f_setcurpl2cpcache(
    [],
    [
        _writeact,
        c.SetMemory(_writeact + 20, c.SetTo, 0),
    ],
)
c.PopTriggerScope()


def _is_consecutive(n: int) -> bool:
    if n == 0:
        return False
    # right shift by index of least significant bit (remove trailing zeros)
    n >>= (n & -n).bit_length() - 1
    return (n & (n + 1)) == 0


def _guess_ordering(bitmask: int, shift: int) -> str:
    lsb_index = (bitmask & -bitmask).bit_length() - 1
    if lsb_index == -shift:
        ordering = "decreasing"
    elif shift == 0:
        ordering = "increasing"
    else:
        ordering = "decreasing"
    return ordering


def _insert(bitmask: int, shift: int, ordering: str | None = None) -> Callable:
    ut.ep_assert(_is_consecutive(bitmask))
    ut.ep_assert(ordering in ("increasing", "decreasing", None))
    if ordering is None:
        ordering = _guess_ordering(bitmask, shift)

    msb_index = bitmask.bit_length() - 1
    lsb_index = (bitmask & -bitmask).bit_length() - 1
    if ordering == "increasing":
        bit_range = range(lsb_index, msb_index + 1)
    else:
        bit_range = range(msb_index, lsb_index - 1, -1)

    def signed_shift(a: int, b: int):
        if b >= 0:
            return a << b
        else:
            return a >> -b

    c.PushTriggerScope()
    _readtrig = [
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 1 << x),
            actions=c.SetMemory(_writeact + 20, c.Add, signed_shift(1, x + shift)),
        )
        for x in bit_range
    ]
    c.SetNextTrigger(_readend)
    c.PopTriggerScope()

    if bitmask not in _table:
        _table[bitmask] = {"increasing": {}, "decreasing": {}}
    _table[bitmask][ordering][shift] = _readtrig
    return _caller(_readtrig[0])


def _get(bitmask: int, shift: int) -> Callable | None:
    ut.ep_assert(_is_consecutive(bitmask))
    msb_index = bitmask.bit_length() - 1
    lsb_index = (bitmask & -bitmask).bit_length() - 1

    for key in _table:
        if key & bitmask == 0:
            continue
        key_msb_index = key.bit_length() - 1
        key_lsb_index = (key & -key).bit_length() - 1
        if key_lsb_index == lsb_index:
            table = _table[key]["decreasing"]
            if shift in table:
                return _caller(table[shift][key_msb_index - msb_index])
        elif key_msb_index == msb_index:
            table = _table[key]["increasing"]
            if shift in table:
                return _caller(table[shift][lsb_index - key_lsb_index])

    return None


def _insert_or_get(
    bitmask: int, shift: int, ordering: str | None = None
) -> Callable:
    readfn = _get(bitmask, shift)
    if readfn is None:
        return _insert(bitmask, shift, ordering)
    return readfn


def _caller(readtrg: c.RawTrigger) -> Callable:
    def f(epd, *, ret=None):
        if ret is None:
            ret = c.EUDVariable()
            ret.makeR()
        else:
            ret = ret[0]
        if c.IsEUDVariable(ret):
            retepd = ut.EPD(ret.getValueAddr())
        else:
            retepd = ret

        nexttrg = c.Forward()
        c.NonSeqCompute(
            [
                (ut.EPD(0x6509B0), c.SetTo, epd),
                (ut.EPD(_readend) + 87 + 8 * 3, c.SetTo, nexttrg),
                (ut.EPD(_writeact) + 4, c.SetTo, retepd),
            ]
        )
        c.SetNextTrigger(readtrg)
        nexttrg << c.NextTrigger()

        return ret

    return f


_insert(0xFFFFFFFF, 0, "decreasing")
_insert(0xFFFFFF00, 0, "increasing")
