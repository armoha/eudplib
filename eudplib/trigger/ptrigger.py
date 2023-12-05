#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Iterable
from typing import TypeAlias

from eudplib import utils as ut

from .. import core as c
from ..core.mapdata.playerinfo import PlayerInfo
from ..core.rawtrigger.constenc import TrgPlayer
from .triggerdef import Actions, Conditions, Trigger

_pinfos: list[PlayerInfo] = []
_pdbtable: dict[bytes, c.Db] = {}

Players: TypeAlias = TrgPlayer | int | Iterable[TrgPlayer | int | Iterable]


def InitPTrigger() -> None:
    """(Internal) Enable PTrigger. Internally called by eudplib"""
    global _pinfos
    if not _pinfos:
        _pinfos = [c.GetPlayerInfo(player) for player in range(8)]


def PTrigger(players: Players, conditions: Conditions = None, actions: Actions = None) -> None:
    """Execute trigger by player basis

    :param players: Players the trigger should execute with. When Current
        Player specifies any of the players, trigger will execute.
    :param conditions: List of conditions. If all conditions are met, then
        actions will be executed.
    :param actions: List of actions.
    """

    InitPTrigger()

    players = ut.FlattenList(players)
    effp: list[bool] = [False] * 8

    # Trigger is never executed if it has no effplayers.
    if len(players) == 0:
        return

    # Check whose the player is executed to.
    for player in players:
        player = c.EncodePlayer(player)

        if 0 <= player <= 7:
            effp[player] = True

        elif 0x12 <= player <= 0x15:  # Force 1 ~ 4
            forceIndex = player - 0x12
            for p in range(8):
                if _pinfos[p].force == forceIndex:
                    effp[p] = True

        elif player == 0x11:  # All players
            for p in range(8):
                effp[p] = True
            break

    # Create player table!
    dbb = b"".join([b"\0\0\0\0" if eff is False else b"aaaa" for eff in effp])
    if dbb in _pdbtable:
        pdb = _pdbtable[dbb]

    else:
        pdb = c.Db(dbb)
        _pdbtable[dbb] = pdb

    # effplayer[p] is True  -> Memory(EPD(pdb) + p) == b'aaaa'
    # effplayer[p] is False -> Memory(EPD(pdb) + p) == b'\0\0\0\0'

    # Create triggers
    offset_curpl = 0x6509B0
    t1, t2, tc, t3 = c.Forward(), c.Forward(), c.Forward(), c.Forward()

    t1 << c.RawTrigger(
        nextptr=t3,
        conditions=c.Memory(offset_curpl, c.AtMost, 7),
        actions=[c.SetNextPtr(t1, t2), c.SetMemory(offset_curpl, c.Add, ut.EPD(pdb))],
    )

    t2 << c.RawTrigger(
        nextptr=t3,
        conditions=c.Deaths(c.CurrentPlayer, c.Exactly, ut.b2i4(b"aaaa"), 0),
        actions=[
            c.SetNextPtr(t2, tc),
            c.SetMemory(offset_curpl, c.Subtract, ut.EPD(pdb)),
        ],
    )

    tc << c.NextTrigger()

    Trigger(conditions, actions)

    c.RawTrigger(actions=[c.SetNextPtr(t2, t3), c.SetMemory(offset_curpl, c.Add, ut.EPD(pdb))])

    t3 << c.RawTrigger(
        actions=[
            c.SetNextPtr(t1, t3),
            c.SetMemory(offset_curpl, c.Subtract, ut.EPD(pdb)),
        ]
    )
