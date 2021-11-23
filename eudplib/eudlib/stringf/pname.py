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
from ...trigger import Trigger
from ..memiof import (
    f_dwread_epd,
    f_wread_epd,
    f_dwbreak,
    f_getcurpl,
    f_setcurpl,
    f_memcmp,
)
from .eudprint import f_dbstr_print, ptr2s, epd2s
from .fmtprint import _format_args
from .cpprint import f_cpstr_print, PName
from .strfunc import f_strlen_epd
from ..utilf import (
    f_playerexist,
    f_getgametick,
    EUDLoopPlayer,
)
from ...localize import _
from ..playerv import PVariable
from ..eudarray import EUDArray
from math import ceil

PLVarUnit, PLVarMask = ceil((0x58F500 - 0x58A364) / 48), 0
PLVarDict = {}


def GetPlayerLightVariable():
    global PLVarUnit, PLVarMask
    ret = (PLVarUnit, 1 << PLVarMask)
    PLVarMask += 1
    if PLVarMask >= 32:
        PLVarMask = 0
        PLVarUnit += 1
    return ret


def compare_sequence(src, seq):
    assert isinstance(src, int) and isinstance(seq, str)
    seq += "\0"
    ret = []
    val, mask = 0, 0

    def append_cmp():
        nonlocal val, mask
        ret.append(c.MemoryX(src - src % 4, c.Exactly, val, mask))
        val, mask = 0, 0

    for char in seq:
        lsh = 8 * (src % 4)
        val += ord(char) << lsh
        mask += 0xFF << lsh
        if src % 4 == 3:
            append_cmp()
        src += 1
    if mask:
        append_cmp()
    return ret


def GetIsPNameCondition(name, _plvars={}):
    try:
        init, end, params = _plvars[name]
    except KeyError:
        c.PushTriggerScope()
        unit, mask = GetPlayerLightVariable()
        init, params = c.NextTrigger(), (c.AtLeast, 1, unit, mask)
        end = c.Forward()
        _plvars[name] = (init, end, params)
        if isinstance(name, str):
            # TODO: only iterate human players
            for player in range(8):
                t = c.RawTrigger(
                    conditions=compare_sequence(0x57EEEB + 36 * player, name),
                    actions=c.SetDeaths(player, c.Add, mask, unit),
                    preserved=False,
                )
        else:
            # TODO: compare every names in a single loop
            for player in EUDLoopPlayer(None):
                equals = f_memcmp(0x57EEEB + 36 * player, name, 25)
                Trigger(
                    conditions=equals.Exactly(0),
                    actions=c.SetDeaths(player, c.Add, mask, unit),
                    preserved=False,
                )
            t = c.RawTrigger()
        end << t
        c.PopTriggerScope()
    return init, end, params


def IsPName(player, name):
    p = c.EncodePlayer(player)
    if isinstance(p, int):
        if p < 8:
            if isinstance(name, str):
                return compare_sequence(0x57EEEB + 36 * p, name)
        else:
            ut.ep_assert(
                p == c.EncodePlayer(c.CurrentPlayer),
                _("IsPName player should be Player1 to Player8 or CurrentPlayer, not {}").format(player),
            )

    init, end, params = GetIsPNameCondition(name)
    if cs.EUDExecuteOnce()():
        # TODO: initialize when game starts
        nptr = c.Forward()
        c.RawTrigger(nextptr=init, actions=c.SetNextPtr(end, nptr))
        nptr << c.NextTrigger()
    cs.EUDEndExecuteOnce()
    return c.DeathsX(p, *params)


class _PlayerName:
    def __init__(self):
        self.is_chatptr_unchanged = c.EUDLightBool()
        self.db = c.Db(218)
        self.ptr, self.epd = c.EUDCreateVariables(2)
        self.odds_or_even = c.EUDLightBool()
        self.name_db_list = [c.Db(26) for _ in range(8)]
        self.basenames, self.baselens = PVariable(self.name_db_list), PVariable()
        self.optimize_start, self.optimize_end = c.Forward(), c.Forward()
        self.odd = [c.Forward() for p in range(8)]
        self.even0 = [c.Forward() for p in range(8)]
        self.even1 = [c.Forward() for p in range(8)]

    def _optimize(self):
        if self.optimize_start.IsSet():
            return

        c.PushTriggerScope()
        prevTxtPtr, _end = c.Forward(), c.Forward()
        self.optimize_start << c.NextTrigger()

        oddA = EUDArray([ut.EPD(x) for x in self.odd])
        even0A = EUDArray([ut.EPD(x) for x in self.even0])
        even1A = EUDArray([ut.EPD(x) for x in self.even1])

        if cs.EUDExecuteOnce()():
            for player in EUDLoopPlayer(None):
                player_name = 36 * player
                playerid_epd = 9 * player
                cs.DoActions(
                    player_name.AddNumber(0x57EEEB),
                    playerid_epd.AddNumber(ut.EPD(0x57EEEC)),
                )
                idlen = f_strlen_epd(playerid_epd)
                nameDb = self.basenames[player]
                f_dbstr_print(nameDb, ptr2s(player_name), ":")
                val_odd = f_dwread_epd(ut.EPD(nameDb))
                v0, v1 = f_dwbreak(val_odd)[0:2]
                val_even0 = v0 * 0x10000
                val_even1 = v1 + f_wread_epd(ut.EPD(nameDb) + 1, 0) * 0x10000
                con_odd, con_even = oddA[player], even1A[player]
                cs.DoActions(
                    idlen.AddNumber(1),  # fix ":" not recognized
                    player_name.AddNumber(1),
                    c.SetMemoryEPD(con_odd + 2, c.SetTo, val_odd),
                    c.SetMemoryEPD(even0A[player] + 2, c.SetTo, val_even0),
                    c.SetMemoryEPD(con_even + 2, c.SetTo, val_even1),
                )
                f_dbstr_print(nameDb, ptr2s(player_name), ":")
                self.baselens[player] = idlen
                if cs.EUDIf()(idlen <= 4):
                    cs.DoActions(
                        c.SetMemoryEPD(con_even + 2, c.SetTo, 0),
                        c.SetMemoryEPD(con_even + 3, c.SetTo, 0x0F000000),
                    )
                    if cs.EUDIf()(idlen <= 2):
                        cs.DoActions(
                            c.SetMemoryEPD(con_odd + 2, c.SetTo, 0),
                            c.SetMemoryEPD(con_odd + 3, c.SetTo, 0x0F000000),
                        )
                    cs.EUDEndIf()
                cs.EUDEndIf()
        cs.EUDEndExecuteOnce()

        once = c.Forward()
        cs.EUDJumpIf([once << c.Memory(0x57F23C, c.Exactly, ~0)], self.optimize_end)
        cs.DoActions(
            self.is_chatptr_unchanged.Clear(),
            c.SetMemory(once + 8, c.SetTo, f_getgametick()),
        )
        c.RawTrigger(
            conditions=[prevTxtPtr << c.Memory(0x640B58, c.Exactly, 11)],
            actions=self.is_chatptr_unchanged.Set(),
        )
        cs.EUDJumpIf(self.is_chatptr_unchanged, _end)
        cs.DoActions(c.SetMemory(prevTxtPtr + 8, c.SetTo, 0))
        for i in range(3, -1, -1):
            c.RawTrigger(
                conditions=c.MemoryX(0x640B58, c.AtLeast, 1, 2 ** i),
                actions=c.SetMemory(prevTxtPtr + 8, c.Add, 2 ** i),
            )
        _end << c.NextTrigger()
        self.optimize_end << c.RawTrigger()
        c.PopTriggerScope()

    def check_id(self, player, dst):
        ret = c.EUDVariable()
        ret << 1

        cs.EUDSwitch(player)
        for i in range(8):
            cs.EUDSwitchCase()(i)
            if cs.EUDIf()(
                [
                    self.odds_or_even.IsCleared(),
                    self.odd[i] << c.MemoryEPD(dst, c.Exactly, 0),
                ]
            ):
                ret << 0

            if cs.EUDElseIf()(
                [
                    self.odds_or_even,
                    self.even0[i] << c.MemoryXEPD(dst, c.Exactly, 0, 0xFFFF0000),
                    self.even1[i] << c.MemoryEPD(dst + 1, c.Exactly, 0),
                ]
            ):
                ret << 0
            cs.EUDEndIf()
            cs.EUDBreak()
        cs.EUDEndSwitch()

        return ret

    def set_pname(self, player, *name):
        self._optimize()

        start = c.Forward()
        c.RawTrigger(
            nextptr=self.optimize_start, actions=c.SetNextPtr(self.optimize_end, start)
        )
        start << c.NextTrigger()

        _end = c.Forward()
        cs.EUDJumpIf(self.is_chatptr_unchanged, _end)
        if ut.isUnproxyInstance(player, type(c.P1)):
            if player == c.CurrentPlayer:
                player = f_getcurpl()
            else:
                player = c.EncodePlayer(player)
        cs.EUDJumpIf(f_playerexist(player) == 0, _end)
        basename, baselen = self.basenames[player], self.baselens[player]

        origcp = f_getcurpl()
        cs.DoActions(
            self.ptr.SetNumber(0x640B61),
            self.epd.SetNumber(ut.EPD(0x640B60)),
            self.odds_or_even.Clear(),
        )
        if cs.EUDWhile()(self.ptr.AtMost(0x640B61 + 218 * 10)):
            cs.EUDContinueIf(f_check_id(player, self.epd))
            cs.EUDContinueIf(f_memcmp(basename, self.ptr, baselen) >= 1)
            cs.DoActions(
                c.SetCurrentPlayer(ut.EPD(self.db)), baselen.SubtractNumber(1)
            )  # fix setpname save 1byte less chat contents
            f_cpstr_print(ptr2s(self.ptr + baselen), EOS=False)
            cs.DoActions(
                c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0),
                baselen.AddNumber(1),
                c.SetCurrentPlayer(self.epd),
            )
            c.RawTrigger(
                conditions=self.odds_or_even.IsSet(),
                actions=[
                    c.SetDeaths(c.CurrentPlayer, c.SetTo, ut.b2i4(b"\r" * 4), 0),
                    c.AddCurrentPlayer(1),
                ],
            )
            name = list(name)
            name.append(epd2s(ut.EPD(self.db)))
            f_cpstr_print(*name)

            cs.EUDSetContinuePoint()
            cs.DoActions(
                self.ptr.AddNumber(218),
                self.epd.AddNumber(54),
                self.odds_or_even.Toggle(),
            )
            c.RawTrigger(
                conditions=self.odds_or_even.IsCleared(), actions=self.epd.AddNumber(1)
            )
        cs.EUDEndWhile()
        f_setcurpl(origcp)

        _end << c.NextTrigger()


_global_pname_class = _PlayerName()


@c.EUDTypedFunc([c.TrgPlayer, None])
def f_check_id(player, dst):
    return _global_pname_class.check_id(player, dst)


def SetPName(player, *name):
    _global_pname_class.set_pname(player, *name)


def SetPNamef(player, format_string, *args):
    fmtargs = _format_args(format_string, *args)
    SetPName(player, *fmtargs)
