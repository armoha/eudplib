#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.constenc import EncodePlayer, PlayerDict, _Player
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import (
    EncodeFlingy,
    EncodeSprite,
    EncodeTech,
    EncodeUnitOrder,
    EncodeUpgrade,
)
from ..localize import _
from .epdoffsetmap import EPDOffsetMap
from .member import ArrayMember
from .memberkind import MemberKind as Mk


class TrgPlayer(_Player, EPDOffsetMap):
    """
    PlayerData is special in the sense that it is not directly related to game data;
    rather, it is intended to deal with various game state specific to players.
    e.g. the amount of gas a player has, can be accessed via PlayerData.
    """

    __slots__ = ()
    mineral = ore = ArrayMember(0x57F0F0, Mk.DWORD)
    gas = ArrayMember(0x57F120, Mk.DWORD)
    cumulativeGas = ArrayMember(0x57F150, Mk.DWORD)
    cumulativeMineral = cumulativeOre = ArrayMember(0x57F180, Mk.DWORD)
    zergControlAvailable = ArrayMember(0x582144, Mk.DWORD)
    zergControlUsed = ArrayMember(0x582174, Mk.DWORD)
    zergControlMax = ArrayMember(0x5821A4, Mk.DWORD)
    terranSupplyAvailable = ArrayMember(0x5821D4, Mk.DWORD)
    terranSupplyUsed = ArrayMember(0x582204, Mk.DWORD)
    terranSupplyMax = ArrayMember(0x582234, Mk.DWORD)
    protossPsiAvailable = ArrayMember(0x582264, Mk.DWORD)
    protossPsiUsed = ArrayMember(0x582294, Mk.DWORD)
    protossPsiMax = ArrayMember(0x5822C4, Mk.DWORD)

    @classmethod
    def cast(cls, other):
        if isinstance(other, cls):
            return other
        if isinstance(other, ConstType):
            raise ut.EPError(
                _('[Warning] "{}" is not a {}').format(other, cls.__name__)
            )
        EPDOffsetMap._cast = True
        return cls(other)

    def __init__(self, initval) -> None:
        super().__init__(EncodePlayer(initval))


# fmt: off
P1, P2, P3, P4 = TrgPlayer(0), TrgPlayer(1), TrgPlayer(2), TrgPlayer(3)
P5, P6, P7, P8 = TrgPlayer(4), TrgPlayer(5), TrgPlayer(6), TrgPlayer(7)
P9, P10, P11, P12 = TrgPlayer(8), TrgPlayer(9), TrgPlayer(10), TrgPlayer(11)
Player1, Player2, Player3, Player4 = P1, P2, P3, P4
Player5, Player6, Player7, Player8 = P5, P6, P7, P8
Player9, Player10, Player11, Player12 = P9, P10, P11, P12
CurrentPlayer = TrgPlayer(13)
Foes, Allies, NeutralPlayers = TrgPlayer(14), TrgPlayer(15), TrgPlayer(16)
AllPlayers = TrgPlayer(17)
Force1, Force2, Force3, Force4 = TrgPlayer(18), TrgPlayer(19), TrgPlayer(20), TrgPlayer(21)  # noqa: E501
NonAlliedVictoryPlayers = TrgPlayer(26)
PlayerDict.update({
    P1: 0, P2: 1, P3: 2, P4: 3,
    P5: 4, P6: 5, P7: 6, P8: 7,
    P9: 8, P10: 9, P11: 10, P12: 11,
    CurrentPlayer: 13,
    Foes: 14, Allies: 15, NeutralPlayers: 16,
    AllPlayers: 17,
    Force1: 18, Force2: 19, Force3: 20, Force4: 21,
    NonAlliedVictoryPlayers: 26,
})
# fmt: on


class Flingy(ConstType, EPDOffsetMap):
    __slots__ = ()
    sprite = ArrayMember(0x6CA318, Mk.SPRITE)
    topSpeed = ArrayMember(0x6C9EF8, Mk.DWORD)
    acceleration = ArrayMember(0x6C9C78, Mk.WORD)
    haltDistance = ArrayMember(0x6C9930, Mk.DWORD)
    turnSpeed = turnRadius = ArrayMember(0x6C9E20, Mk.BYTE)
    # unused = ArrayMember(0x6CA240, Mk.BYTE)
    movementControl = ArrayMember(0x6C9858, Mk.BYTE)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeFlingy(initval))


class Sprite(ConstType, EPDOffsetMap):
    __slots__ = ()
    # Read only data skipped
    image = ArrayMember(0x666160, Mk.IMAGE)
    # hpBarSize = ArrayMember(0x665E50, Mk.BYTE)
    # ??? = ArrayMember(0x666570, Mk.BYTE)
    isVisible = ArrayMember(0x665C48, Mk.BOOL)
    # selectionCircle = ArrayMember(0x665AC0, Mk.BYTE)
    # selectionVerticalOffset = ArrayMember(0x665FD8, Mk.BYTE)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeSprite(initval))


class Upgrade(ConstType, EPDOffsetMap):
    __slots__ = ()
    mineralCostBase = ArrayMember(0x655740, Mk.WORD)
    mineralCostFactor = ArrayMember(0x6559C0, Mk.WORD)
    gasCostBase = ArrayMember(0x655840, Mk.WORD)
    gasCostFactor = ArrayMember(0x6557C0, Mk.WORD)
    timeCostBase = ArrayMember(0x655B80, Mk.WORD)
    timeCostFactor = ArrayMember(0x655940, Mk.WORD)
    requirementOffset = ArrayMember(0x6558C0, Mk.WORD)
    icon = ArrayMember(0x655AC0, Mk.WORD)
    label = ArrayMember(0x655A40, Mk.WORD)
    race = ArrayMember(0x655BFC, Mk.BYTE)
    maxLevel = ArrayMember(0x655700, Mk.BYTE)
    broodWarFlag = ArrayMember(0x655B3C, Mk.BYTE)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeUpgrade(initval))


class Tech(ConstType, EPDOffsetMap):
    __slots__ = ()
    mineralCost = ArrayMember(0x656248, Mk.WORD)
    gasCost = ArrayMember(0x6561F0, Mk.WORD)
    timeCost = ArrayMember(0x6563D8, Mk.WORD)
    energyCost = ArrayMember(0x656380, Mk.WORD)
    # ??? = ArrayMember(0x656198, Mk.WORD)
    requirementOffset = ArrayMember(0x6562F8, Mk.WORD)
    icon = ArrayMember(0x656430, Mk.WORD)
    label = ArrayMember(0x6562A0, Mk.WORD)
    race = ArrayMember(0x656488, Mk.BYTE)
    researched = ArrayMember(0x656350, Mk.BYTE)  # UNUSED?
    broodWarFlag = ArrayMember(0x6564B4, Mk.BYTE)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeTech(initval))


class UnitOrder(ConstType, EPDOffsetMap):
    __slots__ = ()
    label = ArrayMember(0x665280, Mk.WORD)
    useWeaponTargeting = ArrayMember(0x664B00, Mk.BOOL)
    # isSecondaryOrder = ArrayMember(0x665940, Mk.BOOL)
    # nonSubUnit = ArrayMember(0x665A00, Mk.BOOL)
    # ??? = ArrayMember(0x664A40, Mk.BOOL)
    # subUnitcanUse = ArrayMember(0x6657C0, Mk.BOOL)
    canBeInterrupted = ArrayMember(0x665040, Mk.BOOL)
    # ??? = ArrayMember(0x665100, Mk.BOOL)
    canBeQueued = ArrayMember(0x665700, Mk.BOOL)
    # ??? = ArrayMember(0x6651C0, Mk.BOOL)
    canBeObstructed = ArrayMember(0x6654C0, Mk.BOOL)
    # ??? = ArrayMember(0x664C80, Mk.BOOL)
    # requireMoving = ArrayMember(0x664BC0, Mk.BOOL)
    weapon = ArrayMember(0x665880, Mk.WEAPON)
    techUsed = ArrayMember(0x664E00, Mk.TECH)
    animation = ArrayMember(0x664D40, Mk.BYTE)
    buttonIcon = ArrayMember(0x664EC0, Mk.WORD)
    requirementOffset = ArrayMember(0x665580, Mk.WORD)
    obscuredOrder = ArrayMember(0x665400, Mk.UNIT_ORDER)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeUnitOrder(initval))
