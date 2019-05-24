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
from ..memiof import (
    f_dwread_epd,
    f_wread_epd,
    f_dwbreak,
    f_getcurpl,
    f_setcurpl,
    f_memcmp,
)
from .eudprint import f_dbstr_print, ptr2s, epd2s
from .cpprint import f_cpstr_print, PName
from .strfunc import f_strlen_epd
from ..utilf import f_playerexist, EUDPlayerLoop, EUDEndPlayerLoop, f_getgametick, EUDLoopPlayer
from ..playerv import PVariable
from ..eudarray import EUDArray

isPNameInitialized = False

isTxtPtrUnchanged = None
temp_Db = None
ptr, epd = None, None
odds_or_even = None
baselens = None
NameDb = None
baseNames = None
start_optimize = c.Forward()
end_optimize = c.Forward()
odd, even0, even1 = [[c.Forward() for p in range(8)] for _ in range(3)]


def _InitPName():
    global isTxtPtrUnchanged, temp_Db, ptr, epd, temp_Db, odds_or_even
    global baselens, baseNames
    isTxtPtrUnchanged = c.EUDLightVariable()
    temp_Db = c.Db(218)
    ptr, epd = c.EUDVariable(), c.EUDVariable()
    odds_or_even = c.EUDLightVariable()
    baselens = PVariable()
    NameDb = [c.Db(26) for _ in range(8)]
    baseNames = PVariable(NameDb)


@c.EUDFunc
def f_check_id(player, dst):
    ret = c.EUDVariable()
    ret << 1

    cs.EUDSwitch(player)
    for i in range(8):
        cs.EUDSwitchCase()(i)
        if cs.EUDIf()(
            [odds_or_even.Exactly(0), odd[i] << c.MemoryEPD(dst, c.Exactly, 0)]
        ):
            ret << 0

        if cs.EUDElseIf()(
            [
                odds_or_even.Exactly(1),
                even0[i] << c.MemoryXEPD(dst, c.Exactly, 0, 0xFFFF0000),
                even1[i] << c.MemoryEPD(dst + 1, c.Exactly, 0),
            ]
        ):
            ret << 0
        cs.EUDEndIf()
        cs.EUDBreak()
    cs.EUDEndSwitch()

    return ret


def _OptimizeSetPName():
    c.PushTriggerScope()
    global start_optimize, end_optimize, isTxtPtrUnchanged
    prevTxtPtr, _end = c.Forward(), c.Forward()
    start_optimize << c.NextTrigger()

    oddA = EUDArray([ut.EPD(x) for x in odd])
    even0A = EUDArray([ut.EPD(x) for x in even0])
    even1A = EUDArray([ut.EPD(x) for x in even1])

    if cs.EUDExecuteOnce()():
        for player in EUDLoopPlayer(None):
            player_name = 36 * player
            playerid_epd = 9 * player
            cs.DoActions([
                player_name.AddNumber(0x57EEEB),
                playerid_epd.AddNumber(ut.EPD(0x57EEEC)),
            ])
            idlen = f_strlen_epd(playerid_epd)
            nameDb = baseNames[player]
            f_dbstr_print(nameDb, ptr2s(player_name), ":")
            val_odd = f_dwread_epd(ut.EPD(nameDb))
            v0, v1 = f_dwbreak(val_odd)[0:2]
            val_even0 = v0 * 0x10000
            val_even1 = v1 + f_wread_epd(ut.EPD(nameDb) + 1, 0) * 0x10000
            con_odd, con_even = oddA[player], even1A[player]
            cs.DoActions(
                [
                    idlen.AddNumber(1),  # fix ":" not recognized
                    player_name.AddNumber(1),
                    c.SetMemoryEPD(con_odd + 2, c.SetTo, val_odd),
                    c.SetMemoryEPD(even0A[player] + 2, c.SetTo, val_even0),
                    c.SetMemoryEPD(con_even + 2, c.SetTo, val_even1),
                ]
            )
            f_dbstr_print(nameDb, ptr2s(player_name), ":")
            baselens[player] = idlen
            if cs.EUDIf()(idlen <= 4):
                cs.DoActions(
                    [
                        c.SetMemoryEPD(con_even + 2, c.SetTo, 0),
                        c.SetMemoryEPD(con_even + 3, c.SetTo, 0x0F000000),
                    ]
                )
                if cs.EUDIf()(idlen <= 2):
                    cs.DoActions(
                        [
                            c.SetMemoryEPD(con_odd + 2, c.SetTo, 0),
                            c.SetMemoryEPD(con_odd + 3, c.SetTo, 0x0F000000),
                        ]
                    )
                cs.EUDEndIf()
            cs.EUDEndIf()
    cs.EUDEndExecuteOnce()

    once = c.Forward()
    cs.EUDJumpIf([once << c.Memory(0x57F23C, c.Exactly, ~0)], end_optimize)
    cs.DoActions(
        [
            isTxtPtrUnchanged.SetNumber(0),
            c.SetMemory(once + 8, c.SetTo, f_getgametick()),
        ]
    )
    c.RawTrigger(
        conditions=[prevTxtPtr << c.Memory(0x640B58, c.Exactly, 11)],
        actions=isTxtPtrUnchanged.SetNumber(1),
    )
    cs.EUDJumpIf(isTxtPtrUnchanged.Exactly(1), _end)
    cs.DoActions(c.SetMemory(prevTxtPtr + 8, c.SetTo, 0))
    for i in range(3, -1, -1):
        c.RawTrigger(
            conditions=c.MemoryX(0x640B58, c.AtLeast, 1, 2 ** i),
            actions=c.SetMemory(prevTxtPtr + 8, c.Add, 2 ** i),
        )
    _end << c.NextTrigger()
    end_optimize << c.RawTrigger()
    c.PopTriggerScope()


def SetPName(player, *name):
    global isPNameInitialized
    if not isPNameInitialized:
        _InitPName()
        _OptimizeSetPName()
        isPNameInitialized = True

    start = c.Forward()
    c.RawTrigger(nextptr=start_optimize, actions=[c.SetNextPtr(end_optimize, start)])
    start << c.NextTrigger()

    _end = c.Forward()
    cs.EUDJumpIf(isTxtPtrUnchanged.Exactly(1), _end)
    if ut.isUnproxyInstance(player, type(c.P1)):
        if player == c.CurrentPlayer:
            player = f_getcurpl()
        else:
            player = c.EncodePlayer(player)
    cs.EUDJumpIf(f_playerexist(player) == 0, _end)
    basename, baselen = baseNames[player], baselens[player]

    global ptr, epd, odds_or_even
    origcp = f_getcurpl()
    cs.DoActions(
        [
            ptr.SetNumber(0x640B61),
            epd.SetNumber(ut.EPD(0x640B60)),
            odds_or_even.SetNumber(0),
        ]
    )
    if cs.EUDWhile()(ptr.AtMost(0x640B61 + 218 * 10)):
        cs.EUDContinueIf(f_check_id(player, epd))
        cs.EUDContinueIf(f_memcmp(basename, ptr, baselen) >= 1)
        cs.DoActions([
            c.SetCurrentPlayer(ut.EPD(temp_Db)),
            baselen.SubtractNumber(1),
        ])  # fix setpname save 1byte less chat contents
        f_cpstr_print(ptr2s(ptr + baselen), EOS=False)
        cs.DoActions([
            c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
            baselen.AddNumber(1),
            c.SetCurrentPlayer(epd),
        ])
        c.RawTrigger(
            conditions=odds_or_even.Exactly(1),
            actions=[
                c.SetDeaths(c.CurrentPlayer, c.SetTo, ut.b2i4(b"\r" * 4), 0),
                c.AddCurrentPlayer(1),
            ],
        )
        f_cpstr_print(*(name + (epd2s(ut.EPD(temp_Db)),)))

        cs.EUDSetContinuePoint()
        cs.DoActions(
            [ptr.AddNumber(218), epd.AddNumber(54), odds_or_even.AddNumberX(1, 1)]
        )
        c.RawTrigger(conditions=odds_or_even.Exactly(0), actions=epd.AddNumber(1))
    cs.EUDEndWhile()
    f_setcurpl(origcp)

    _end << c.NextTrigger()
