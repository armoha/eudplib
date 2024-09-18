# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable

from .. import core as c
from .. import utils as ut
from . import modcurpl as cp

consecutive_table: dict[int, dict[int, dict[int, c.RawTrigger]]] = {}

c.PushTriggerScope()
copy_ret = c.SetDeaths(0, c.SetTo, 0, 0)
read_end_common = c.RawTrigger(
    nextptr=0,
    actions=[
        copy_ret,
        c.SetMemory(copy_ret + 20, c.SetTo, 0),
    ],
)
c.PopTriggerScope()


def _is_consecutive(n: int) -> bool:
    # right shift by index of least significant bit (remove trailing zeros)
    n >>= (n & -n).bit_length() - 1
    return (n & (n + 1)) == 0


def guess_ordering(bitmask: int, shift: int) -> bool:
    lsb_index = (bitmask & -bitmask).bit_length() - 1
    if lsb_index == -shift:
        return True
    elif shift == 0:
        return False
    else:
        return True


def signed_shift(a: int, b: int):
    if b >= 0:
        return a << b
    else:
        return a >> -b


def _insert(bitmask: int, shift: int, is_decreasing: bool | None = None) -> Callable:
    ut.ep_assert(_is_consecutive(bitmask))
    ut.ep_assert(is_decreasing in (True, False, None))
    if is_decreasing is None:
        is_decreasing: bool = guess_ordering(bitmask, shift)

    msb_index: int = bitmask.bit_length() - 1
    lsb_index = (bitmask & -bitmask).bit_length() - 1
    if is_decreasing:
        startswith, endswith = msb_index, lsb_index
    else:
        startswith, endswith = lsb_index, msb_index

    try:
        shift_table = consecutive_table[shift]
    except KeyError:
        shift_table = {}
        consecutive_table[shift] = shift_table
    try:
        trig_table = shift_table[endswith]
    except KeyError:
        trig_table = {}
        shift_table[endswith] = trig_table
    try:
        start_trig = trig_table[startswith]
    except KeyError:
        c.PushTriggerScope()
        step = 1 if is_decreasing else -1
        for x in range(endswith, startswith + step, step):
            if x not in trig_table:
                trig = c.RawTrigger(
                    nextptr=read_end_common
                    if x == endswith
                    else trig_table[x - step],
                    conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 1 << x),
                    actions=c.SetMemory(
                        copy_ret + 20, c.Add, signed_shift(1, x + shift)
                    ),
                )
                trig_table[x] = trig
        c.PopTriggerScope()
        start_trig = trig_table[startswith]

    return _epd_caller(start_trig)


def _get(bitmask: int, shift: int) -> Callable | None:
    ut.ep_assert(_is_consecutive(bitmask))
    msb_index = bitmask.bit_length() - 1
    lsb_index = (bitmask & -bitmask).bit_length() - 1

    shift_table = consecutive_table[shift]
    try:
        trig_table = shift_table[lsb_index]
    except KeyError:
        trig_table = shift_table[msb_index]
        return _epd_caller(trig_table[lsb_index])
    else:
        return _epd_caller(trig_table[msb_index])


def _insert_or_get(
    bitmask: int, shift: int, ordering: bool | None = None
) -> Callable:
    try:
        return _get(bitmask, shift)
    except KeyError:
        return _insert(bitmask, shift, ordering)


def _epd_caller(readtrg: c.RawTrigger) -> Callable:
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
                (ut.EPD(read_end_common) + 87 + 8 * 3, c.SetTo, nexttrg),
                (ut.EPD(copy_ret) + 4, c.SetTo, retepd),
            ]
        )
        c.SetNextTrigger(readtrg)
        nexttrg << c.NextTrigger()

        return ret

    return f


_insert(0xFFFFFFFF, 0, True)
_insert(0xFFFFFF00, 0, False)
