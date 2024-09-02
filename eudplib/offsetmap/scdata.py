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
    EncodeImage,
    EncodeSprite,
    EncodeTech,
    EncodeUnit,
    EncodeUnitOrder,
    EncodeUpgrade,
    EncodeWeapon,
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


class TrgUnit(ConstType, EPDOffsetMap):
    __slots__ = ()
    graphic = flingy = ArrayMember(0x6644F8, Mk.FLINGY)
    subUnit = ArrayMember(0x6607C0, Mk.UNIT)
    # subunit2 is unused
    # subunit2 = ArrayMember(0x660C38, Mk.WORD)
    # infestationUnit is not implemented yet. (different beginning index)
    # SCBW_DATA(u16*,		InfestedUnitPartial,	unitsDat[3].address);
    # 0x664980, (Id - UnitId::TerranCommandCenter) for it to work,
    # last valid id is UnitId::Special_OvermindCocoon
    constructionGraphic = ArrayMember(0x6610B0, Mk.IMAGE, stride=4)
    startDirection = ArrayMember(0x6605F0, Mk.BYTE)
    hasShield = ArrayMember(0x6647B0, Mk.BOOL)
    maxShield = ArrayMember(0x660E00, Mk.WORD)
    maxHp = ArrayMember(0x662350, Mk.DWORD)
    elevation = ArrayMember(0x663150, Mk.BYTE)
    movementFlags = ArrayMember(0x660FC8, Mk.BYTE)
    rank = ArrayMember(0x663DD0, Mk.BYTE)
    computerIdleOrder = ArrayMember(0x662EA0, Mk.UNIT_ORDER)
    humanIdleOrder = ArrayMember(0x662268, Mk.UNIT_ORDER)
    returnToIdleOrder = ArrayMember(0x664898, Mk.UNIT_ORDER)
    attackUnitOrder = ArrayMember(0x663320, Mk.UNIT_ORDER)
    attackMoveOrder = ArrayMember(0x663A50, Mk.UNIT_ORDER)
    groundWeapon = ArrayMember(0x6636B8, Mk.WEAPON)
    maxGroundHits = ArrayMember(0x6645E0, Mk.BYTE)
    airWeapon = ArrayMember(0x6616E0, Mk.WEAPON)
    maxAirHits = ArrayMember(0x65FC18, Mk.BYTE)
    # FIXME: split 2 flags into separate members
    AIFlags = ArrayMember(0x660178, Mk.BYTE)
    baseProperty = ArrayMember(0x664080, Mk.DWORD)  # FIXME: should be enum
    seekRange = ArrayMember(0x662DB8, Mk.BYTE)
    sightRange = ArrayMember(0x663238, Mk.BYTE)
    armorUpgrade = ArrayMember(0x6635D0, Mk.UPGRADE)
    sizeType = ArrayMember(0x662180, Mk.BYTE)  # FIXME: should be enum
    armor = ArrayMember(0x65FEC8, Mk.BYTE)
    rightClickAction = ArrayMember(0x662098, Mk.BYTE)  # FIXME: should be enum
    readySound = ArrayMember(0x661FC0, Mk.WORD)
    whatSoundStart = ArrayMember(0x65FFB0, Mk.WORD)
    whatSoundEnd = ArrayMember(0x662BF0, Mk.WORD)
    pissedSoundStart = ArrayMember(0x663B38, Mk.WORD)
    pissedSoundEnd = ArrayMember(0x661EE8, Mk.WORD)
    yesSoundStart = ArrayMember(0x663C10, Mk.WORD)
    yesSoundEnd = ArrayMember(0x661440, Mk.WORD)
    buildingDimensions = ArrayMember(0x662860, Mk.POSITION)
    # AddonPlacement is not implemented yet because its beginning index isn't 0.
    # addonPlacement = ArrayMember(0x6626E0, Mk.POSITION)
    # unitDimensions is not implemented yet.
    # unitBoundsLURB = ArrayMember(0x6617C8, 2 * Mk.POSITION)
    portrait = ArrayMember(0x662F88, Mk.WORD)  # FIXME: should be PORTRAIT
    mineralCost = ArrayMember(0x663888, Mk.WORD)
    gasCost = ArrayMember(0x65FD00, Mk.WORD)
    timeCost = ArrayMember(0x660428, Mk.WORD)
    requirementOffset = ArrayMember(0x660A70, Mk.WORD)
    groupFlags = ArrayMember(0x6637A0, Mk.BYTE)
    supplyProvided = ArrayMember(0x6646C8, Mk.BYTE)
    supplyUsed = ArrayMember(0x663CE8, Mk.BYTE)
    transportSpaceProvided = ArrayMember(0x660988, Mk.BYTE)
    transportSpaceRequired = ArrayMember(0x664410, Mk.BYTE)
    buildScore = ArrayMember(0x663408, Mk.WORD)
    killScore = ArrayMember(0x663EB8, Mk.WORD)
    nameString = ArrayMember(0x660260, Mk.WORD)
    broodWarFlag = ArrayMember(0x6606D8, Mk.BYTE)
    stareditAvailabilityFlags = ArrayMember(0x661528, Mk.WORD)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeUnit(initval))


class Weapon(ConstType, EPDOffsetMap):
    __slots__ = ()
    label = ArrayMember(0x6572E0, Mk.WORD)  # FIXME: should be STATTEXT
    graphic = flingy = ArrayMember(0x656CA8, Mk.FLINGY)
    # special attack is for reference only?
    # specialAttack = ArrayMember(0x6573E8, Mk.BYTE)
    targetFlags = ArrayMember(0x657998, Mk.WORD)  # FIXME: should be enum
    # can't use range because it's a python keyword
    minRange = ArrayMember(0x656A18, Mk.DWORD)
    maxRange = ArrayMember(0x657470, Mk.DWORD)
    upgrade = ArrayMember(0x6571D0, Mk.UPGRADE)
    damageType = ArrayMember(0x657258, Mk.BYTE)  # FIXME: should be enum
    # Fly and follow target, appear on target unit, etc.
    behavior = ArrayMember(0x656670, Mk.BYTE)
    removeAfter = ArrayMember(0x657040, Mk.BYTE)
    explosionType = ArrayMember(0x6566F8, Mk.BYTE)  # FIXME: should be enum
    splashInnerRadius = ArrayMember(0x656888, Mk.WORD)
    splashMiddleRadius = ArrayMember(0x6570C8, Mk.WORD)
    splashOuterRadius = ArrayMember(0x657780, Mk.WORD)
    damage = ArrayMember(0x656EB0, Mk.WORD)
    damageBonus = ArrayMember(0x657678, Mk.WORD)
    cooldown = ArrayMember(0x656FB8, Mk.BYTE)
    damageFactor = ArrayMember(0x6564E0, Mk.BYTE)
    attackAngle = ArrayMember(0x656990, Mk.BYTE)
    launchSpin = ArrayMember(0x657888, Mk.BYTE)
    forwardOffset = graphicXOffset = ArrayMember(0x657910, Mk.BYTE)
    verticalOffset = graphicYOffset = ArrayMember(0x656C20, Mk.BYTE)
    targetErrorMessage = ArrayMember(0x656568, Mk.WORD)  # FIXME: should be STATTEXT
    icon = ArrayMember(0x656780, Mk.WORD)  # FIXME: should be ICON

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeWeapon(initval))


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


class Image(ConstType, EPDOffsetMap):
    __slots__ = ()
    # Read only data skipped
    # grpFile = ArrayMember(0x668AA0, Mk.DWORD)
    isTurnable = graphicTurn = ArrayMember(0x66E860, Mk.BOOL)
    isClickable = ArrayMember(0x66C150, Mk.BOOL)
    useFullIscript = ArrayMember(0x66D4D8, Mk.BOOL)
    drawIfCloaked = ArrayMember(0x667718, Mk.BOOL)
    drawingFunction = ArrayMember(0x669E28, Mk.BYTE)  # FIXME: it should be enum
    # Remapping table is skipped because it doesn't work in SC:R
    # FIXME: Add UnsupportedMember
    # remapping = ArrayMember(0x669A40, Mk.BYTE)
    iscript = ArrayMember(0x66EC48, Mk.DWORD)  # FIXME: should be ISCRIPT
    # shieldsOverlay = ArrayMember(0x66C538, Mk.DWORD)
    # attackOverlay = ArrayMember(0x66B1B0, Mk.DWORD)
    # damageOverlay = ArrayMember(0x66A210, Mk.DWORD)
    # specialOverlay = ArrayMember(0x667B00, Mk.DWORD)
    # landingDustOverlay = ArrayMember(0x666778, Mk.DWORD)
    # liftOffDustOverlay = ArrayMember(0x66D8C0, Mk.DWORD)

    @classmethod
    def cast(cls, s):
        if isinstance(s, cls):
            return s
        if isinstance(s, ConstType):
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, cls.__name__))
        EPDOffsetMap._cast = True
        return cls(s)

    def __init__(self, initval) -> None:
        super().__init__(EncodeImage(initval))


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
