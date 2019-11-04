#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

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

import random

from ... import core as c, ctrlstru as cs, utils as ut

from .modcurpl import f_setcurpl2cpcache
from ...core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from ...core.variable.evcommon import _ev


@_EUDPredefineReturn(_ev[:2])
@_EUDPredefineParam(_ev[2:3])
@c.EUDFunc
def f_dwepdread_epd(targetplayer):
    ptr, epd = f_dwepdread_epd._frets
    u = random.randint(234, 65535)
    acts = [
        ptr.SetNumber(0),
        epd.SetNumber(ut.EPD(0)),
        targetplayer.AddNumber(-12 * u),
        targetplayer.SetDest(ut.EPD(0x6509B0)),
    ]
    random.shuffle(acts)
    c.VProc(targetplayer, acts)

    r = list(range(31, -1, -1))
    random.shuffle(r)
    for i in r:
        acts = [ptr.AddNumber(2 ** i), epd.AddNumber(2 ** (i - 2)) if i >= 2 else []]
        random.shuffle(acts)
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, u, 2 ** i), actions=acts
        )

    f_setcurpl2cpcache()

    # return ptr, epd


@_EUDPredefineReturn(_ev[:1])
@_EUDPredefineParam(_ev[1:2])
@c.EUDFunc
def f_dwread_epd(targetplayer):
    ptr = f_dwread_epd._frets[0]
    u = random.randint(234, 65535)
    acts = [
        ptr.SetNumber(0),
        targetplayer.AddNumber(-12 * u),
        targetplayer.SetDest(ut.EPD(0x6509B0)),
    ]
    random.shuffle(acts)
    c.VProc(targetplayer, acts)
    r = list(range(31, -1, -1))
    random.shuffle(r)
    for i in r:
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, u, 2 ** i),
            actions=ptr.AddNumber(2 ** i),
        )

    f_setcurpl2cpcache()

    # return ptr


def f_epdread_epd(targetplayer):
    return f_dwepdread_epd(targetplayer)[1]


# Special flag reading functions
def f_flagread_epd(targetplayer, *flags, _readerdict={}):
    flags = tuple(flags)  # Make flags hashable

    if flags in _readerdict:
        readerf = _readerdict[flags]
    else:
        # Create reader function
        @c.EUDFunc
        def readerf(targetplayer):
            flagsv = [c.EUDVariable() for _ in flags]

            # All set to 0
            c.VProc(
                targetplayer,
                [
                    targetplayer.SetDest(ut.EPD(0x6509B0)),
                    [flagv.SetNumber(0) for flagv in flagsv],
                ],
            )

            # Fill flags
            for i in range(31, -1, -1):
                bitandflags = [flag & (2 ** i) for flag in flags]
                if sum(bitandflags) == 0:
                    continue
                c.RawTrigger(
                    conditions=[c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** i)],
                    actions=[
                        flagv.AddNumber(2 ** i)
                        for j, flagv in enumerate(flagsv)
                        if flags[j] & (2 ** i)
                    ],
                )

            f_setcurpl2cpcache()

            return flagsv

        _readerdict[flags] = readerf

    return readerf(targetplayer)


# Writing functions


def f_dwwrite_epd(targetplayer, value):
    cs.DoActions(c.SetDeaths(targetplayer, c.SetTo, value, 0))


def f_dwadd_epd(targetplayer, value):
    cs.DoActions(c.SetDeaths(targetplayer, c.Add, value, 0))


def f_dwsubtract_epd(targetplayer, value):
    cs.DoActions(c.SetDeaths(targetplayer, c.Subtract, value, 0))


# Dword breaking functions
@c.EUDFunc
def f_dwbreak(number):
    """Get hiword/loword/4byte of dword"""
    word = [c.EUDXVariable(0, 0xFFFF), c.EUDVariable()]
    byte = [c.EUDXVariable(0, 0xFF)] + c.EUDCreateVariables(3)

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

    r = list(range(31, 7, -1))
    random.shuffle(r)
    for i in r:
        byteidx = i // 8
        wordidx = i // 16
        byteexp = i % 8
        wordexp = i % 16

        c.RawTrigger(
            conditions=number.AtLeastX(1, 2 ** i),
            actions=[
                byte[byteidx].AddNumber(2 ** byteexp),
                [word[wordidx].AddNumber(2 ** wordexp) if wordidx == 1 else []],
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
f_dwepdread_epd_safe = f_dwepdread_epd
f_dwread_epd_safe = f_dwread_epd
f_epdread_epd_safe = f_epdread_epd
