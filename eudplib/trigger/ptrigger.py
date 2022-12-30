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

from eudplib import utils as ut

from .. import core as c
from .triggerdef import Trigger

_pt_db = c.Db
_pinfos = None
_pdbtable = {}


def InitPTrigger() -> None:
    """(Internal) Enable PTrigger. Internally called by eudplib"""
    global _pinfos
    if _pinfos is None:
        _pinfos = [c.GetPlayerInfo(player) for player in range(8)]


def PTrigger(players, conditions=None, actions=None) -> None:
    """Execute trigger by player basis

    :param players: Players the trigger should execute with. When Current
        Player specifies any of the players, trigger will execute.
    :param conditions: List of conditions. If all conditions are met, then
        actions will be executed.
    :param actions: List of actions.
    """

    InitPTrigger()

    players = ut.FlattenList(players)
    effp = [False] * 8

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
