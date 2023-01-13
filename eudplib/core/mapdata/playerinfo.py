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
from eudplib.core.mapdata.chktok import CHK


class PlayerInfo:
    def __init__(self) -> None:
        self.force: int
        self.race: int
        self.type: int
        self.racestr: str
        self.typestr: str


_playerinfo: list[PlayerInfo] = []


def InitPlayerInfo(chkt: CHK) -> None:
    _playerinfo.clear()

    section_forc = chkt.getsection("FORC")
    section_ownr = chkt.getsection("OWNR")
    section_side = chkt.getsection("SIDE")

    for player in range(8):
        pinfo = PlayerInfo()
        _playerinfo.append(pinfo)

        # Numeric info
        pinfo.force = section_forc[player]
        pinfo.race = section_side[player]
        pinfo.type = section_ownr[player]

        # String info
        pinfo.racestr = {
            0x00: "Zerg",
            0x01: "Terran",
            0x02: "Protoss",
            0x03: "Independent",
            0x04: "Neutral",
            0x05: "User selectable",
            0x07: "Inactive",
            0x08: "Human",
            0x0A: "Human",
            0x0D: "Starcraft Campaign Editor",
        }.get(pinfo.race, "")

        pinfo.typestr = {
            0x00: "Unused",
            0x03: "Rescuable",
            0x05: "Computer",
            0x06: "Human",
            0x07: "Neutral",
        }.get(pinfo.type, "")


def GetPlayerInfo(player) -> PlayerInfo:
    from eudplib.core.rawtrigger.constenc import EncodePlayer

    return _playerinfo[EncodePlayer(player)]
