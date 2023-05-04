#!/usr/bin/python
# Copyright 2022 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..utils import EPD, ep_assert
from .rawtrigger import (
    Add,
    CurrentPlayer,
    EncodePlayer,
    RawTrigger,
    SetDeaths,
    SetMemory,
    SetMemoryEPD,
    SetMemoryX,
    SetMemoryXEPD,
    SetTo,
    Subtract,
)
from .variable import IsEUDVariable, VProc


def cpset(a, b):
    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        return a + b, RawTrigger
    elif IsEUDVariable(a) and IsEUDVariable(b):
        VProc(
            [a, b],
            [
                a.QueueAssignTo(EPD(0x6509B0)),
                b.QueueAddTo(EPD(0x6509B0)),
            ],
        )
    else:
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            a,
            [
                SetMemory(0x6509B0, SetTo, b),
                a.QueueAddTo(EPD(0x6509B0)),
            ],
        )
    from ..eudlib.memiof.modcurpl import f_setcurpl2cpcache

    return EncodePlayer(CurrentPlayer), f_setcurpl2cpcache


def iset(a, b, modifier, v):
    """SetMemoryEPD(a + b, modifier, v)"""
    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        from ..eudlib.memiof.dwepdio import setdw_epd

        return setdw_epd(a + b, modifier, v)
    if IsEUDVariable(v):
        if IsEUDVariable(a) and IsEUDVariable(b):
            return VProc(
                [a, b, v],
                [
                    a.QueueAssignTo(EPD(v.getDestAddr())),
                    b.QueueAddTo(EPD(v.getDestAddr())),
                    v.SetModifier(modifier),
                ],
            )
        if IsEUDVariable(b):
            a, b = b, a
        return VProc(
            [a, v],
            [
                v.SetDest(b),
                a.QueueAddTo(EPD(v.getDestAddr())),
                v.SetModifier(modifier),
            ],
        )
    set_v = SetDeaths(0, modifier, v, 0)
    if IsEUDVariable(a) and IsEUDVariable(b):
        VProc(
            [a, b],
            [
                a.QueueAssignTo(EPD(set_v) + 4),
                b.QueueAddTo(EPD(set_v) + 4),
            ],
        )
    else:
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            a,
            [
                SetMemory(set_v + 16, SetTo, b),
                a.QueueAddTo(EPD(set_v) + 4),
            ],
        )
    return RawTrigger(actions=set_v)


def isub(a, b, v):
    if not IsEUDVariable(v):
        return iset(a, b, Add, -v)
    dst, trg = cpset(a, b)
    VProc(
        v,
        [
            SetMemoryXEPD(dst, Add, -1, 0x55555555),
            SetMemoryXEPD(dst, Add, -1, 0xAAAAAAAA),
            SetMemoryEPD(dst, Add, 1),
            v.QueueAddTo(dst),
        ],
    )
    return trg(
        actions=[
            SetMemoryXEPD(dst, Add, -1, 0x55555555),
            SetMemoryXEPD(dst, Add, -1, 0xAAAAAAAA),
            SetMemoryEPD(dst, Add, 1),
        ],
    )


def iand(a, b, v):
    if not IsEUDVariable(v):
        if not (IsEUDVariable(a) or IsEUDVariable(b)):
            return RawTrigger(actions=SetMemoryXEPD(a + b, SetTo, 0, ~v))

        write = SetMemoryXEPD(0, SetTo, 0, ~v)
        if IsEUDVariable(a) and IsEUDVariable(b):
            VProc(
                [a, b],
                [
                    a.QueueAssignTo(EPD(write) + 4),
                    b.QueueAddTo(EPD(write) + 4),
                ],
            )
        else:
            if IsEUDVariable(b):
                a, b = b, a
            VProc(
                a,
                [
                    SetMemory(write + 16, SetTo, b),
                    a.QueueAddTo(EPD(write) + 4),
                ],
            )
        return RawTrigger(actions=write)

    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        write = SetMemoryXEPD(a + b, SetTo, 0, 0)
        VProc(v, v.QueueAssignTo(EPD(write)))
    elif IsEUDVariable(a) and IsEUDVariable(b):
        write = SetMemoryXEPD(0, SetTo, 0, 0)
        VProc(
            [a, b, v],
            [
                a.QueueAssignTo(EPD(write) + 4),
                b.QueueAddTo(EPD(write) + 4),
                v.QueueAssignTo(EPD(write)),
            ],
        )
    else:
        write = SetMemoryXEPD(0, SetTo, 0, 0)
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            [a, v],
            [
                SetMemory(write + 16, SetTo, b),
                a.QueueAddTo(EPD(write) + 4),
                v.QueueAssignTo(EPD(write)),
            ],
        )
    return RawTrigger(
        actions=[
            SetMemoryX(write, Add, -1, 0x55555555),
            SetMemoryX(write, Add, -1, 0xAAAAAAAA),
            write,
        ],
    )


def ior(a, b, v):
    if not IsEUDVariable(v):
        if not (IsEUDVariable(a) or IsEUDVariable(b)):
            return RawTrigger(actions=SetMemoryXEPD(a + b, SetTo, ~0, v))

        write = SetMemoryXEPD(0, SetTo, ~0, v)
        if IsEUDVariable(a) and IsEUDVariable(b):
            VProc(
                [a, b],
                [
                    a.QueueAssignTo(EPD(write) + 4),
                    b.QueueAddTo(EPD(write) + 4),
                ],
            )
        else:
            if IsEUDVariable(b):
                a, b = b, a
            VProc(
                a,
                [
                    SetMemory(write + 16, SetTo, b),
                    a.QueueAddTo(EPD(write) + 4),
                ],
            )
        return RawTrigger(actions=write)

    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        write = SetMemoryXEPD(a + b, SetTo, ~0, 0)
        VProc(v, v.QueueAssignTo(EPD(write)))
        return RawTrigger(actions=write)

    write = SetMemoryXEPD(0, SetTo, ~0, 0)
    if IsEUDVariable(a) and IsEUDVariable(b):
        VProc(
            [a, b, v],
            [
                a.QueueAssignTo(EPD(write) + 4),
                b.QueueAddTo(EPD(write) + 4),
                v.QueueAssignTo(EPD(write)),
            ],
        )
    else:
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            [a, v],
            [
                SetMemory(write + 16, SetTo, b),
                a.QueueAddTo(EPD(write) + 4),
                v.QueueAssignTo(EPD(write)),
            ],
        )
    return RawTrigger(actions=write)


def ixor(a, b, v):
    if not IsEUDVariable(v):
        dst, trg = cpset(a, b)
        return trg(
            actions=[
                SetMemoryXEPD(dst, Add, v, 0x55555555),
                SetMemoryXEPD(dst, Add, v, 0xAAAAAAAA),
            ],
        )

    dst = EPD(v.getDestAddr())
    if not (IsEUDVariable(a) or IsEUDVariable(b)):
        VProc(v, [v.QueueAddTo(a + b), v.SetMask(0x55555555)])
    elif IsEUDVariable(a) and IsEUDVariable(b):
        VProc(
            [a, b, v],
            [
                a.QueueAssignTo(dst),
                b.QueueAddTo(dst),
                v.SetMask(0x55555555),
                v.SetModifier(Add),
            ],
        )
    else:
        if IsEUDVariable(b):
            a, b = b, a
        VProc(
            [a, v],
            [
                a.QueueAddTo(dst),
                v.QueueAddTo(b),
                v.SetMask(0x55555555),
            ],
        )
    VProc(v, v.SetMask(0xAAAAAAAA))
    # FIXME: restore to previous mask???
    return RawTrigger(actions=v.SetMask(0xFFFFFFFF))


def ilshift(a, b, n):
    ep_assert(isinstance(n, int))
    if n == 0:
        return
    mask = (1 << (n + 1)) - 1
    dst, trg = cpset(a, b)
    itemw = lambda mod, value, mask: SetMemoryXEPD(dst, mod, value, mask)
    return trg(
        actions=[
            [
                itemw(SetTo, 0, (mask >> 1) << (n + 1)),
                itemw(Add, (mask >> 1) << n, mask << n),
            ]
            for n in reversed(range(32 - n))
        ]
        + [itemw(SetTo, 0, mask >> 1)]  # lowest n bits
    )


def irshift(a, b, n):
    ep_assert(isinstance(n, int))
    if n == 0:
        return
    mask = (1 << (n + 1)) - 1
    dst, trg = cpset(a, b)
    sub = lambda value, mask: SetMemoryXEPD(dst, Subtract, value, mask)
    return trg(
        actions=[SetMemoryXEPD(dst, SetTo, 0, mask >> 1)]  # lowest n bits
        + [sub((mask >> 1) << n, mask << n) for n in range(32 - n)]
    )
