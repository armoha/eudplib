# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib.core.mapdata.chktok import CHK


class PlayerInfo:
    def __init__(self) -> None:
        self.force: int
        self.race: int
        self.type: int
        self.racestr: str
        self.typestr: str


_playerinfo: list[PlayerInfo] = []


def init_player_info(chkt: CHK) -> None:
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


def GetPlayerInfo(player) -> PlayerInfo:  # noqa: N802
    from eudplib.core.rawtrigger.constenc import EncodePlayer

    return _playerinfo[EncodePlayer(player)]
