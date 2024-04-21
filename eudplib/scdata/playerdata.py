#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ..core.rawtrigger import constenc
from ..utils import unProxy
from .member import Member, MemberKind, PlayerDataMember
from .scdataobject import SCDataObject


class PlayerData(SCDataObject):
    """
    PlayerData is special in the sense that it is not directly related to game data;
    rather, it is intended to deal with various game state specific to players.
    e.g. the amount of gas a player has, can be accessed via PlayerData.
    """

    mineral = ore = Member(0x57F0F0, MemberKind.DWORD)
    gas = Member(0x57F120, MemberKind.DWORD)
    cumulativeGas = Member(0x57F150, MemberKind.DWORD)  # noqa: N815
    cumulativeMineral = cumulativeOre = Member(0x57F180, MemberKind.DWORD)  # noqa: N815
    zergControlAvailable = Member(0x582144, MemberKind.DWORD)  # noqa: N815
    zergControlUsed = Member(0x582174, MemberKind.DWORD)  # noqa: N815
    zergControlMax = Member(0x5821A4, MemberKind.DWORD)  # noqa: N815
    terranSupplyAvailable = Member(0x5821D4, MemberKind.DWORD)  # noqa: N815
    terranSupplyUsed = Member(0x582204, MemberKind.DWORD)  # noqa: N815
    terranSupplyMax = Member(0x582234, MemberKind.DWORD)  # noqa: N815
    protossPsiAvailable = Member(0x582264, MemberKind.DWORD)  # noqa: N815
    protossPsiUsed = Member(0x582294, MemberKind.DWORD)  # noqa: N815
    protossPsiMax = Member(0x5822C4, MemberKind.DWORD)  # noqa: N815
    # SCBW_DATA(Units12*,     firstPlayerUnit,        0x006283F8);
    # Contains various information (names, player types, race types, and forces)
    # of each player in the current game
    # SCBW_DATA(const PLAYER*,  playerTable,          0x0057EEE0);

    # playerAlliance, playerVision? (needs a pair of players)

    def __init__(self, index):
        unproxied = unProxy(index)
        if isinstance(unproxied, int):
            index = unproxied
        super().__init__(constenc.EncodePlayer(index))


PlayerDataMember._data_object_type = PlayerData
