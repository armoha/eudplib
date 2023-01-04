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

import functools
from typing import TYPE_CHECKING, overload

from .. import core as c
from ..core import ConstExpr, EUDVariable
from ..ctrlstru import EUDJumpIf
from ..localize import _
from ..utils import EPError, ExprProxy, unProxy

if TYPE_CHECKING:
    from ..core.rawtrigger.constenc import Player, _Player
    from ..eudlib import EUDArray

_runner_start: "list[c.Forward]" = [c.Forward() for _ in range(8)]
_runner_end: "list[c.Forward]" = [c.Forward() for _ in range(8)]

_runner_cp: c.EUDLightVariable = c.EUDLightVariable()

c.PushTriggerScope()
for player in range(8):
    _runner_start[player] << c.RawTrigger(nextptr=_runner_end[player])
    _runner_end[player] << c.RawTrigger(nextptr=~(0x51A280 + player * 12 + 4))
c.PopTriggerScope()


@c.EUDFunc
def RunTrigTrigger() -> None:
    from .. import eudlib as sf

    oldcp = sf.f_getcurpl()

    for player in range(8):
        skipt = c.Forward()
        EUDJumpIf(
            c.Memory(0x51A280 + 12 * player + 4, c.Exactly, 0x51A280 + 12 * player + 4),
            skipt,
        )
        nt = c.Forward()
        c.RawTrigger(
            nextptr=_runner_start[player],
            actions=[
                c.SetMemory(0x6509B0, c.SetTo, player),
                _runner_cp.SetNumber(player),
                c.SetNextPtr(_runner_end[player], nt),
            ],
        )
        nt << c.RawTrigger(
            actions=c.SetNextPtr(_runner_end[player], ~(0x51A280 + player * 12 + 4))
        )
        skipt << c.NextTrigger()

    sf.f_setcurpl(oldcp)


#######


@functools.cache
def AllocTrigTriggerLink() -> "tuple[EUDArray, EUDArray, EUDArray]":
    from .. import eudlib as sf

    return sf.EUDArray(8), sf.EUDArray(8), sf.EUDArray(_runner_end)


def GetFirstTrigTrigger(player: "Player") -> EUDVariable:
    """Get dlist start of trig-trigger for player"""
    player = c.EncodePlayer(player)
    orig_tstart, _orig_tend, _runner_end_array = AllocTrigTriggerLink()
    return orig_tstart[player]


def GetLastTrigTrigger(player: "Player") -> EUDVariable:
    """Get dlist end of trig-trigger for player"""
    player = c.EncodePlayer(player)
    _orig_tstart, orig_tend, _runner_end_array = AllocTrigTriggerLink()
    return orig_tend[player]


def TrigTriggerBegin(player: "Player") -> EUDVariable:
    return GetFirstTrigTrigger(player)


@overload
def TrigTriggerEnd(player: "int | _Player | ExprProxy[int | _Player]") -> c.Forward:
    ...


@overload
def TrigTriggerEnd(
    player: EUDVariable | ConstExpr | ExprProxy[EUDVariable | ConstExpr],
) -> EUDVariable:
    ...


def TrigTriggerEnd(player):
    _orig_tstart, _orig_tend, runner_end_array = AllocTrigTriggerLink()
    player = c.EncodePlayer(player)
    if isinstance(player, int):
        return _runner_end[player]
    return runner_end_array[player]
