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
    # struct SupplyData {
    # u32 provided[PLAYER_COUNT];
    # u32 used[PLAYER_COUNT];
    # u32 max[PLAYER_COUNT];
    # SCBW_DATA(Units12*,     firstPlayerUnit,        0x006283F8);
    # Contains various information (names, player types, race types, and associated forces)
    # of each player in the current game
    # SCBW_DATA(const PLAYER*,  playerTable,          0x0057EEE0);

    # playerAlliance, playerVision? (needs a pair of players)

    def __init__(self, index):
        unproxied = unProxy(index)
        if isinstance(unproxied, int):
            index = unproxied
        super().__init__(constenc.EncodePlayer(index))


PlayerDataMember._data_object_type = PlayerData
