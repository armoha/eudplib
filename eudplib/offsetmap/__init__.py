#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .csprite import CSprite
from .cunit import CUnit, EPDCUnitMap
from .epdoffsetmap import EPDOffsetMap
from .member import (
    BaseMember,
    CSpriteMember,
    CUnitMember,
    EnumMember,
    Flag,
    Member,
    MemberKind,
    UnsupportedMember,
)

# fmt: off
from .scdata import (
    Flingy,
    Image,
    Sprite,
    Tech,
    TrgUnit,
    UnitOrder,
    Upgrade,
    Weapon,
    TrgPlayer,
    P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12,
    Force1, Force2, Force3, Force4, AllPlayers, CurrentPlayer,
    Allies, Foes, NeutralPlayers, NonAlliedVictoryPlayers,
)

__all__ = [
    "CSprite",
    "CUnit",
    "EPDCUnitMap",
    "EPDOffsetMap",
    "BaseMember",
    "CSpriteMember",
    "CUnitMember",
    "EnumMember",
    "Flag",
    "Member",
    "MemberKind",
    "UnsupportedMember",
    "Flingy",
    "Image",
    "Sprite",
    "Tech",
    "TrgUnit",
    "UnitOrder",
    "Upgrade",
    "Weapon",
    "TrgPlayer",
    "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12",
    "Force1", "Force2", "Force3", "Force4", "AllPlayers", "CurrentPlayer",
    "Allies", "Foes", "NeutralPlayers", "NonAlliedVictoryPlayers",
]
# fmt: on
