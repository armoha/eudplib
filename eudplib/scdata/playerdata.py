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

    def __init__(self, index):
        unproxied = unProxy(index)
        if isinstance(unproxied, int):
            index = unproxied
        super().__init__(constenc.EncodePlayer(index))

PlayerDataMember._data_object_type = PlayerData
