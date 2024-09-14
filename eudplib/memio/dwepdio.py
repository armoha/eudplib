#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import random
import warnings

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from ..localize import _
from . import iotable
from . import modcurpl as cp


@_EUDPredefineReturn(2)
@_EUDPredefineParam(cp.CP)
@c.EUDFunc
def f_dwepdread_epd(targetplayer):
    ptr, epd = f_dwepdread_epd._frets
    u = random.randint(234, 65535)
    acts = [
        ptr.SetNumber(0),
        epd.SetNumber(ut.EPD(0)),
        c.SetMemory(0x6509B0, c.Add, -12 * u),
    ]
    cs.DoActions(ut._rand_lst(acts))

    for i in ut._rand_lst(range(32)):
        acts = [
            ptr.AddNumber(2**i),
            epd.AddNumber(2 ** (i - 2)) if i >= 2 else [],
        ]
        c.RawTrigger(
            conditions=c.DeathsX(cp.CP, c.AtLeast, 1, u, 2**i),
            actions=ut._rand_lst(acts),
        )

    cp.f_setcurpl2cpcache()

    # return ptr, epd


def f_dwread_epd(targetplayer, *, ret=None):
    return iotable._get(0xFFFFFFFF, 0)(targetplayer, ret=ret)


@_EUDPredefineReturn(1)
@_EUDPredefineParam(cp.CP)
@c.EUDFunc
def f_epdread_epd(targetplayer):
    ptr = f_epdread_epd._frets[0]
    u = random.randint(234, 65535)
    acts = [
        ptr.SetNumber(ut.EPD(0)),
        c.SetMemory(0x6509B0, c.Add, -12 * u),
    ]
    cs.DoActions(ut._rand_lst(acts))
    for i in ut._rand_lst(range(2, 32)):
        c.RawTrigger(
            conditions=c.DeathsX(cp.CP, c.AtLeast, 1, u, 2**i),
            actions=ptr.AddNumber(2 ** (i - 2)),
        )

    cp.f_setcurpl2cpcache()

    # return ptr


# Special flag reading functions
def f_flagread_epd(targetplayer, *flags, _readerdict={}):
    flags = tuple(flags)  # Make flags hashable

    if flags in _readerdict:
        readerf = _readerdict[flags]
    else:
        # Create reader function
        @_EUDPredefineParam(cp.CP)
        @c.EUDFunc
        def readerf(targetplayer):
            flagsv = c.EUDCreateVariables(len(flags))

            # All set to 0
            cs.DoActions([flagv.SetNumber(0) for flagv in flagsv])

            # Fill flags
            for i in range(31, -1, -1):
                bitandflags = [flag & (2**i) for flag in flags]
                if sum(bitandflags) == 0:
                    continue
                c.RawTrigger(
                    conditions=[c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**i)],
                    actions=[
                        flagv.AddNumber(2**i)
                        for j, flagv in enumerate(flagsv)
                        if flags[j] & (2**i)
                    ],
                )

            cp.f_setcurpl2cpcache()

            return flagsv

        _readerdict[flags] = readerf

    return readerf(targetplayer)


# Writing functions


def setdw_epd(targetplayer, modifier, value):
    if c.IsEUDVariable(value):
        if c.IsEUDVariable(targetplayer):
            if targetplayer is value:
                c.VProc(
                    value,
                    [
                        value.SetDest(value),
                        value.SetModifier(c.SetTo),
                    ],
                )
                return c.VProc(value, value.SetModifier(modifier))
            return c.VProc(
                [targetplayer, value],
                [
                    targetplayer.QueueAssignTo(ut.EPD(value.getDestAddr())),
                    value.SetModifier(modifier),
                ],
            )
        return c.VProc(
            value,
            [
                value.SetDest(targetplayer),
                value.SetModifier(modifier),
            ],
        )
    cs.DoActions(c.SetDeaths(targetplayer, modifier, value, 0))


def f_dwwrite_epd(targetplayer, value):
    setdw_epd(targetplayer, c.SetTo, value)


def f_dwadd_epd(targetplayer, value):
    setdw_epd(targetplayer, c.Add, value)


def f_dwsubtract_epd(targetplayer, value):
    setdw_epd(targetplayer, c.Subtract, value)


# Dword breaking functions
@c.EUDFunc
def f_dwbreak(number):
    """Get hiword/loword/4byte of dword"""
    word = [c.EUDXVariable(0, c.SetTo, 0, 0xFFFF), c.EUDVariable()]
    byte = [c.EUDXVariable(0, c.SetTo, 0, 0xFF), *c.EUDCreateVariables(3)]

    # Clear byte[], word[]
    c.VProc(
        [number, word[0]],
        [
            number.SetDest(word[0]),
            word[0].SetDest(byte[0]),
            word[1].SetNumber(0),
            byte[1].SetNumber(0),
            byte[2].SetNumber(0),
            byte[3].SetNumber(0),
        ],
    )

    for i in ut._rand_lst(range(8, 32)):
        byteidx = i // 8
        wordidx = i // 16
        byteexp = i % 8
        wordexp = i % 16

        c.RawTrigger(
            conditions=number.AtLeastX(1, 2**i),
            actions=[
                byte[byteidx].AddNumber(2**byteexp),
                word[wordidx].AddNumber(2**wordexp) if wordidx == 1 else [],
            ],
        )

    return word[0], word[1], byte[0], byte[1], byte[2], byte[3]


@c.EUDFunc
def f_dwbreak2(number):
    """Get hiword/loword/4byte of dword"""
    word = c.EUDCreateVariables(2)
    byte = c.EUDCreateVariables(4)

    # Set byte[], word[]
    c.VProc(
        [number, word[0], word[1], byte[0], byte[1], byte[2]],
        [
            number.SetDest(word[0]),
            word[0].SetDest(word[1]),
            word[1].SetDest(byte[0]),
            byte[0].SetDest(byte[1]),
            byte[1].SetDest(byte[2]),
            byte[2].SetDest(byte[3]),
        ],
    )
    c.RawTrigger(
        actions=[
            word[0].SetNumberX(0, ~0xFFFF),
            word[1].SetNumberX(0, 0xFFFF),
            byte[0].SetNumberX(0, ~0xFF),
            byte[1].SetNumberX(0, ~0xFF00),
            byte[2].SetNumberX(0, ~0xFF0000),
            byte[3].SetNumberX(0, 0xFFFFFF),
        ]
    )

    return word[0], word[1], byte[0], byte[1], byte[2], byte[3]


# backward compatibility functions
E = _("safe read functions are deprecated in 0.61 and will be removed in 0.63")


def f_dwepdread_epd_safe(*args, **kwargs):
    warnings.warn(E, DeprecationWarning)
    return f_dwepdread_epd(*args, **kwargs)


def f_dwread_epd_safe(*args, **kwargs):
    warnings.warn(E, DeprecationWarning)
    return f_dwread_epd(*args, **kwargs)


def f_epdread_epd_safe(*args, **kwargs):
    warnings.warn(E, DeprecationWarning)
    return f_epdread_epd(*args, **kwargs)
