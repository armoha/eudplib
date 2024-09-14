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
from .offsetmap import (
    ArrayEnumMember,
    ArrayMember,
    EPDOffsetMap,
    Flag,
    NotImplementedMember,
)
from .offsetmap import MemberKind as Mk


# FIXME: integrate with CUnit MovementFlags
class MovementFlags(ArrayEnumMember):
    __slots__ = ()
    OrderedAtLeastOnce = Flag(0x01)
    Accelerating = Flag(0x02)
    Braking = Flag(0x04)
    StartingAttack = Flag(0x08)
    Moving = Flag(0x10)
    Lifted = Flag(0x20)
    BrakeOnPathStep = Flag(0x40)
    "unit decelerates when reaching the end of current path segment"
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


class BaseProperty(ArrayEnumMember):
    """SpecialAbilityFlag in PyMS, UnitPrototypeFlags in bwapi, BaseProperty in GPTP"""  # noqa: E501

    __slots__ = ()
    Building = Flag(0x00000001)
    Addon = Flag(0x00000002)
    Flyer = Flag(0x00000004)
    Worker = Flag(0x00000008)
    "resource_miner in PyMS"
    Subunit = Flag(0x00000010)
    FlyingBuilding = Flag(0x00000020)
    Hero = Flag(0x00000040)
    RegeneratesHp = Flag(0x00000080)
    AnimatedIdle = Flag(0x00000100)
    Cloakable = Flag(0x00000200)
    TwoUnitsInOneEgg = Flag(0x00000400)
    SingleEntity = Flag(0x00000800)  # NeutralAccessories in GPTP
    "prevents multi-select, set on all pickup items"
    ResourceDepot = Flag(0x00001000)
    "Place where resources are brought back"
    ResourceContainer = Flag(0x00002000)
    "Resource Source"
    Robotic = Flag(0x00004000)
    Detector = Flag(0x00008000)
    Organic = Flag(0x00010000)
    RequiresCreep = Flag(0x00020000)
    Unused = Flag(0x00040000)
    RequiresPsi = Flag(0x00080000)
    Burrowable = Flag(0x00100000)
    Spellcaster = Flag(0x00200000)
    PermanentCloak = Flag(0x00400000)
    PickupItem = Flag(0x00800000)
    "data disc, crystals, mineral chunks, gas tanks, etc."
    IgnoresSupplyCheck = Flag(0x01000000)
    "MorphFromOtherUnit in GPTP"
    MediumOverlay = Flag(0x02000000)
    "Used to determine overlay for various spells and effects"
    LargeOverlay = Flag(0x04000000)
    AutoAttackAndMove = Flag(0x08000000)
    "battle_reactions in PyMS"
    CanAttack = Flag(0x10000000)
    "full_auto_attack in PyMS"
    Invincible = Flag(0x20000000)
    Mechanical = Flag(0x40000000)
    ProducesUnits = Flag(0x80000000)
    "It can produce units directly (making buildings doesn't count)"


class AvailabilityFlags(ArrayEnumMember):
    __slots__ = ()
    NonNeutral = Flag(0x001)
    UnitListing = Flag(0x002)
    "set availability to be created by CreateUnit action"
    MissionBriefing = Flag(0x004)
    PlayerSettings = Flag(0x008)
    AllRaces = Flag(0x010)
    SetDoodadState = Flag(0x020)
    NonLocationTriggers = Flag(0x040)
    UnitHeroSettings = Flag(0x080)
    LocationTriggers = Flag(0x100)
    BroodWarOnly = Flag(0x200)


class TrgUnit(ConstType, EPDOffsetMap):
    __slots__ = ()
    graphic = flingy = ArrayMember(0x6644F8, Mk.FLINGY)
    subUnit = ArrayMember(0x6607C0, Mk.UNIT)
    # subunit2 = ArrayMember(0x660C38, Mk.WORD)
    # subunit2 is unused
    # infestationUnit is not implemented yet (different beginning index)
    # SCBW_DATA(u16*, InfestedUnitPartial, unitsDat[3].address);
    # 0x664980, (Id - UnitId::TerranCommandCenter) for it to work,
    # last valid id is UnitId::Special_OvermindCocoon
    constructionGraphic = ArrayMember(0x6610B0, Mk.IMAGE, stride=4)
    startDirection = ArrayMember(0x6605F0, Mk.BYTE)  # 0~31, 32
    hasShield = ArrayMember(0x6647B0, Mk.BOOL)
    maxShield = ArrayMember(0x660E00, Mk.WORD)
    maxHp = ArrayMember(0x662350, Mk.DWORD)
    elevation = ArrayMember(0x663150, Mk.BYTE)
    movementFlags = MovementFlags(0x660FC8, Mk.BYTE)
    rank = ArrayMember(0x663DD0, Mk.RANK)
    computerIdleOrder = ArrayMember(0x662EA0, Mk.UNIT_ORDER)
    humanIdleOrder = ArrayMember(0x662268, Mk.UNIT_ORDER)
    returnToIdleOrder = ArrayMember(0x664898, Mk.UNIT_ORDER)
    attackUnitOrder = ArrayMember(0x663320, Mk.UNIT_ORDER)
    attackMoveOrder = ArrayMember(0x663A50, Mk.UNIT_ORDER)
    groundWeapon = ArrayMember(0x6636B8, Mk.WEAPON)
    airWeapon = ArrayMember(0x6616E0, Mk.WEAPON)
    maxGroundHits = ArrayMember(0x6645E0, Mk.BYTE)
    """(read-only) Maximum number of hits this unit can deal to ground targets.

    This attribute represents the maximum number of hits this unit can inflict on a
    target with its ground weapon. For example, the Psi Blades have a `damageFactor`
    of 1, while the Zealot has a `maxGroundHits` of 2. The actual number of attacks
    is determined by the iscript.

    유닛이 지상 무기로 대상을 타격할 수 있는 최대 명중 횟수입니다. 예를 들어,
    사이오닉 검의 `damageFactor`는 1이고 질럿의 `maxGroundHits`은 2입니다.
    실제 공격 횟수는 iscript에서 결정됩니다.
    """
    maxAirHits = ArrayMember(0x65FC18, Mk.BYTE)
    """(read-only) Maximum number of hits this unit can deal to air targets.

    This attribute represents the maximum number of hits this unit can inflict on a
    target with its air weapon. For example, Halo Rockets have a `damageFactor` of 2,
    while the Valkyrie has a `maxAirHits` of 4. The actual number of attacks is
    determined by the iscript.

    유닛이 공중 무기로 대상을 타격할 수 있는 최대 명중 횟수입니다. 예를 들어, 광륜
    로켓의 `damageFactor`는 최대치인 2이고 발키리의 `maxAirHits`은 4입니다. 실제 공격
    횟수는 iscript에서 결정됩니다.
    """
    ignoreStrategicSuicideMissions = ArrayMember(0x660178, Mk.BOOL)
    """Flag indicating whether the unit is excluded from Strategic Suicide Missions.

    When `ignoreStrategicSuicideMissions` is enabled, the unit will be excluded from
    Strategic Suicide Missions. Disabling this flag does not have a noticeable effect
    . By default, `ignoreStrategicSuicideMissions` and `dontBecomeGuard` are either
    both enabled or both disabled for every unit.

    `ignoreStrategicSuicideMissions`가 활성화되면 해당 유닛이 Strategic Suicide
    Missions에서 제외됩니다. 이 플래그를 비활성화해도 눈에 띄는 효과는 없습니다.
    기본적으로 모든 유닛에서 `ignoreStrategicSuicideMissions`와 `dontBecomeGuard`는
    둘 다 켜져있거나 둘 다 꺼져있습니다.
    """
    dontBecomeGuard = ArrayMember(0x660178, Mk.BIT_1)
    """Flag to prevent unit from returning to original position when target disappears.

    Enabling `dontBecomeGuard` can cause game crashes, especially if the CPU controls
    the unit. This flag prevents the unit from returning to its original position if
    the target disappears, but does not affect units that already exist. It primarily
    impacts units with AI ptr type 1 or 4, which are subject to Strategic Suicide
    Missions. Units with this flag set will only be assigned AI if they have
    `baseProperty.Worker` (becoming unitAI type 2), or if they have
    `baseProperty.Building` and are not geysers, or are larva/egg/overlord (becoming
    unitAI type 3).

    `dontBecomeGuard`를 활성화하면 특히 CPU가 유닛을 제어할 때 게임이 크래시할 수
    있습니다. 이 플래그는 명령 대상이 사라졌을 때 유닛이 원래 위치로 돌아가는 것을
    방지합니다. 이미 존재하는 유닛에는 영향을 주지 않습니다. 이 플래그는 주로 AI ptr
    타입 1 또는 4가 있는 유닛에 영향을 미치며, 이러한 유닛은 Strategic Suicide
    Missions에 대상이 됩니다. 이 플래그가 설정된 유닛은 `baseProperty.Worker`가
    있거나 (유닛 AI 타입 2가 됨), `baseProperty.Building`이 있고 베스핀 간헐천이
    아니거나, 라바/에그/오버로드인 경우 (유닛AI 타입 3이 됨) AI가 할당됩니다.
    """  # noqa: E501
    baseProperty = BaseProperty(0x664080, Mk.DWORD)
    seekRange = ArrayMember(0x662DB8, Mk.BYTE)
    sightRange = ArrayMember(0x663238, Mk.BYTE)
    armorUpgrade = ArrayMember(0x6635D0, Mk.UPGRADE)
    sizeType = ArrayMember(0x662180, Mk.UNIT_SIZE)
    armor = ArrayMember(0x65FEC8, Mk.BYTE)
    rightClickAction = ArrayMember(0x662098, Mk.RCLICK_ACTION)
    readySound = ArrayMember(0x661FC0, Mk.SFXDATA_DAT)
    whatSoundStart = ArrayMember(0x65FFB0, Mk.SFXDATA_DAT)
    whatSoundEnd = ArrayMember(0x662BF0, Mk.SFXDATA_DAT)
    pissedSoundStart = ArrayMember(0x663B38, Mk.SFXDATA_DAT)
    pissedSoundEnd = ArrayMember(0x661EE8, Mk.SFXDATA_DAT)
    yesSoundStart = ArrayMember(0x663C10, Mk.SFXDATA_DAT)
    yesSoundEnd = ArrayMember(0x661440, Mk.SFXDATA_DAT)
    buildingDimensions = ArrayMember(0x662860, Mk.POSITION)
    addonPlacement = NotImplementedMember(0x6626E0, Mk.POSITION)
    """AddonPlacement is not implemented yet because its beginning index isn't 0."""
    # unitBoundsLURB = NotImplementedMember(0x6617C8, 2 * Mk.POSITION)
    # """unitDimensions is not implemented yet."""
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
    nameString = ArrayMember(0x660260, Mk.MAP_STRING)
    broodWarFlag = ArrayMember(0x6606D8, Mk.BYTE)  # bool?
    availabilityFlags = AvailabilityFlags(0x661518, Mk.WORD)

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
