#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from .. import utils as ut
from ..core.rawtrigger.consttype import ConstType
from ..core.rawtrigger.strenc import EncodeUnit
from ..localize import _
from .enummember import ArrayEnumMember, Flag
from .epdoffsetmap import EPDOffsetMap
from .member import ArrayMember
from .memberkind import MemberKind as Mk


# FIXME: integrate with CUnit MovementFlags
class MovementFlags(ArrayEnumMember):
    __slots__ = ()
    OrderedAtLeastOnce = Flag(0x01)
    Accelerating = Flag(0x02)
    Braking = Flag(0x04)
    StartingAttack = Flag(0x08)
    Moving = Flag(0x10)
    Lifted = Flag(0x20)
    Unknown = Flag(0x40)
    AlwaysZero = Flag(0x80)
    HoverUnit = Flag(0xC1)


class GroupFlags(ArrayEnumMember):
    __slots__ = ()
    Zerg = Flag(0x01)
    Terran = Flag(0x02)
    Protoss = Flag(0x04)
    Men = Flag(0x08)
    Building = Flag(0x10)
    Factory = Flag(0x20)
    Independent = Flag(0x40)
    Neutral = Flag(0x80)


class BaseProperty(ArrayEnumMember):  # UnitPrototypeFlags in bwapi
    __slots__ = ()
    Building = Flag(0x00000001)
    Addon = Flag(0x00000002)
    Flyer = Flag(0x00000004)
    Worker = Flag(0x00000008)
    Subunit = Flag(0x00000010)
    FlyingBuilding = Flag(0x00000020)
    Hero = Flag(0x00000040)
    RegeneratesHP = Flag(0x00000080)
    AnimatedIdle = Flag(0x00000100)
    Cloakable = Flag(0x00000200)
    TwoUnitsIn1Egg = Flag(0x00000400)
    # AKA "Single entity" (prevents multi-select, set on all pickup items)
    NeutralAccessories = Flag(0x00000800)
    ResourceDepot = Flag(0x00001000)  # Place where resources are brought back
    ResourceContainer = Flag(0x00002000)  # Resource Source
    RoboticUnit = Flag(0x00004000)
    Detector = Flag(0x00008000)
    Organic = Flag(0x00010000)
    CreepBuilding = Flag(0x00020000)
    Unused = Flag(0x00040000)
    RequiredPsi = Flag(0x00080000)
    Burrowable = Flag(0x00100000)
    Spellcaster = Flag(0x00200000)
    PermanentCloak = Flag(0x00400000)
    # AKA "Pickup item" (data disc, crystals, mineral chunks, gas tanks, etc.)
    NPCOrAccessories = Flag(0x00800000)
    MorphFromOtherUnit = Flag(0x01000000)
    # Used to determine overlay for various spells and effects
    MediumOverlay = Flag(0x02000000)
    LargeOverlay = Flag(0x04000000)
    AutoAttackAndMove = Flag(0x08000000)
    CanAttack = Flag(0x10000000)
    Invincible = Flag(0x20000000)
    Mechanical = Flag(0x40000000)
    # It can produce units directly (making buildings doesn't count)
    ProducesUnits = Flag(0x80000000)


class StareditAvailabilityFlags(ArrayEnumMember):
    __slots__ = ()
    NonNeutral = Flag(0x001)
    # set availability to be created by CreateUnit action
    UnitListingAndPalette = Flag(0x002)
    MissionBriefing = Flag(0x004)
    PlayerSettings = Flag(0x008)
    AllRaces = Flag(0x010)
    SetDoodadState = Flag(0x020)
    NonLocationTriggers = Flag(0x040)
    UnitAndHeroSettings = Flag(0x080)
    LocationTriggers = Flag(0x100)
    BroodWarOnly = Flag(0x200)


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
    movementFlags = MovementFlags(0x660FC8, Mk.BYTE)
    rank = ArrayMember(0x663DD0, Mk.BYTE)  # FIXME: should be RANK subset of STATTEXT
    computerIdleOrder = ArrayMember(0x662EA0, Mk.UNIT_ORDER)
    humanIdleOrder = ArrayMember(0x662268, Mk.UNIT_ORDER)
    returnToIdleOrder = ArrayMember(0x664898, Mk.UNIT_ORDER)
    attackUnitOrder = ArrayMember(0x663320, Mk.UNIT_ORDER)
    attackMoveOrder = ArrayMember(0x663A50, Mk.UNIT_ORDER)
    groundWeapon = ArrayMember(0x6636B8, Mk.WEAPON)
    maxGroundHits = ArrayMember(0x6645E0, Mk.BYTE)
    airWeapon = ArrayMember(0x6616E0, Mk.WEAPON)
    maxAirHits = ArrayMember(0x65FC18, Mk.BYTE)
    # this is unrelated to strategic suicide mission; it's only checked with units
    # that have already been added to an attack wave, and looks like it prevents
    # those units from being counted as being missing from the attack group or
    # something like that. i'm not fully understanding its purpose yet and not seeing
    # much of a noticeable effect by ticking it on for regular military units
    # ignoreStrategicSuicideMissions = ArrayMember(0x660178, Mk.BOOL)

    # dontBecomeGuard affects unit's eligibility for strategic suicide missions;
    # basically if a unit has an AI ptr that is type 1 or 4, it will be picked up for
    # strategic suicide. units with flag 2 set only have an AI assigned to them if
    # they have the worker unitsdat property (becomes unitAI type 2), or has building
    # unitsdat property and isn't geyser, or is unitid larva/egg/overlord (becomes
    # unitAI type 3)
    dontBecomeGuard = ArrayMember(0x660178, Mk.BIT_1)
    baseProperty = BaseProperty(0x664080, Mk.DWORD)
    seekRange = ArrayMember(0x662DB8, Mk.BYTE)
    sightRange = ArrayMember(0x663238, Mk.BYTE)
    armorUpgrade = ArrayMember(0x6635D0, Mk.UPGRADE)
    sizeType = ArrayMember(0x662180, Mk.BYTE)  # FIXME: should be enum
    armor = ArrayMember(0x65FEC8, Mk.BYTE)
    rightClickAction = ArrayMember(0x662098, Mk.BYTE)  # FIXME: should be enum
    readySound = ArrayMember(0x661FC0, Mk.WORD)  # sfxdata.dat start index
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
    portrait = ArrayMember(0x662F88, Mk.PORTRAIT)
    mineralCost = ArrayMember(0x663888, Mk.WORD)
    gasCost = ArrayMember(0x65FD00, Mk.WORD)
    timeCost = ArrayMember(0x660428, Mk.WORD)
    requirementOffset = ArrayMember(0x660A70, Mk.WORD)
    groupFlags = GroupFlags(0x6637A0, Mk.BYTE)
    supplyProvided = ArrayMember(0x6646C8, Mk.BYTE)
    supplyUsed = ArrayMember(0x663CE8, Mk.BYTE)
    transportSpaceProvided = ArrayMember(0x660988, Mk.BYTE)
    transportSpaceRequired = ArrayMember(0x664410, Mk.BYTE)
    buildScore = ArrayMember(0x663408, Mk.WORD)
    killScore = ArrayMember(0x663EB8, Mk.WORD)
    nameString = ArrayMember(0x660260, Mk.W_STRING)  # WORD
    broodWarFlag = ArrayMember(0x6606D8, Mk.BYTE)  # bool?
    stareditAvailabilityFlags = StareditAvailabilityFlags(0x661518, Mk.WORD)

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
