# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

import functools
from collections.abc import Iterator
from typing import TYPE_CHECKING

from .. import core as c
from ..collections import EUDArray
from ..core import EUDVariable
from ..ctrlstru import EUDEndIf, EUDIfNot, EUDJumpIf

if TYPE_CHECKING:
    from ..core.rawtrigger.typehint import Player

_runner_start: list[c.Forward] = [c.Forward() for _ in range(8)]
_runner_end: list[c.Forward] = [c.Forward() for _ in range(8)]

_runner_cp: c.EUDLightVariable = c.EUDLightVariable()

c.PushTriggerScope()
for player in range(8):
    _runner_start[player] << c.RawTrigger(nextptr=_runner_end[player])
    _runner_end[player] << c.RawTrigger(nextptr=~(0x51A280 + player * 12 + 4))
c.PopTriggerScope()


@c.EUDFunc
def RunTrigTrigger() -> None:  # noqa: N802
    from ..memio import f_getcurpl, f_setcurpl

    oldcp = f_getcurpl()

    for player in range(8):
        skipt = c.Forward()
        EUDJumpIf(
            c.Memory(
                0x51A280 + 12 * player + 4,
                c.Exactly,
                0x51A280 + 12 * player + 4,
            ),
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

    f_setcurpl(oldcp)


#######


@functools.cache
def _alloc_trigtrigger_link() -> tuple[EUDArray, EUDArray, EUDArray]:
    return EUDArray(8), EUDArray(8), EUDArray(_runner_end)


def GetFirstTrigTrigger(player: Player) -> EUDVariable:  # noqa: N802
    """Get dlist start of trig-trigger for player"""
    player = c.EncodePlayer(player)
    orig_tstart, _orig_tend, _runner_end_array = _alloc_trigtrigger_link()
    return orig_tstart[player]


def GetLastTrigTrigger(player: Player) -> EUDVariable:  # noqa: N802
    """Get dlist end of trig-trigger for player"""
    player = c.EncodePlayer(player)
    _orig_tstart, orig_tend, _runner_end_array = _alloc_trigtrigger_link()
    return orig_tend[player]


def TrigTriggerBegin(player: Player) -> EUDVariable:  # noqa: N802
    return GetFirstTrigTrigger(player)


def TrigTriggerEnd(player: Player) -> c.Forward | EUDVariable:  # noqa: N802
    _orig_tstart, _orig_tend, runner_end_array = _alloc_trigtrigger_link()
    player = c.EncodePlayer(player)
    if isinstance(player, int):
        return _runner_end[player]
    return runner_end_array[player]


#######


def EUDLoopTrigger(player) -> Iterator[tuple[EUDVariable, EUDVariable]]:  # noqa: N802
    from ..eudlib.utilf.listloop import EUDLoopList

    player = c.EncodePlayer(player)

    tbegin = TrigTriggerBegin(player)
    if EUDIfNot()(tbegin == 0):
        tend = TrigTriggerEnd(player)
        yield from EUDLoopList(tbegin, tend)
    EUDEndIf()
