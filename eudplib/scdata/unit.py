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
    """u8: Flags that enable/disable certain movement."""

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
    """Uses underlings, can build on creep"""
    Terran = Flag(0x02)
    """Uses Supply, has sublabel, buildings will burn"""
    Protoss = Flag(0x04)
    """Uses Psi"""
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
    "Resource Source. Can be selected by `ModifyUnitResourceAmount` action."
    Robotic = Flag(0x00004000)
    Detector = Flag(0x00008000)
    Organic = Flag(0x00010000)
    RequiresCreep = Flag(0x00020000)
    Unused = Flag(0x00040000)
    RequiresPsi = Flag(0x00080000)
    Burrowable = Flag(0x00100000)
    Spellcaster = Flag(0x00200000)
    "Can be selected by `ModifyUnitEnergy` action"
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
    flingy = ArrayMember(0x6644F8, Mk.FLINGY)
    "Flingy: Flingy of unit. 유닛의 비행정보."
    subUnit = ArrayMember(0x6607C0, Mk.UNIT)
    "TrgUnit: Subunit of unit. 유닛의 부가유닛"
    # subunit2 = ArrayMember(0x660C38, Mk.WORD)
    # subunit2 is unused. 유닛의 두번째 부가유닛. 사용되지 않습니다.
    # infestationUnit is not implemented yet (different beginning index)
    # SCBW_DATA(u16*, InfestedUnitPartial, unitsDat[3].address);
    # 0x664980, (Id - UnitId::TerranCommandCenter) for it to work,
    # last valid id is UnitId::Special_OvermindCocoon
    # 퀸이 감염 시켰을 경우 바뀌는 대상 유닛. 106-201 (건물)에만 존재합니다.
    constructionGraphic = ArrayMember(0x6610B0, Mk.IMAGE, stride=4)
    """Image: Sets the graphic when the unit is built.

    유닛이 건설될 때의 그래픽을 설정합니다.
    """
    startDirection = ArrayMember(0x6605F0, Mk.BYTE)
    """u8: Direction unit will face after it is created.

    Values start at 0 (the unit will face the top of the screen) and go on clockwise
    through subsequent turning stages until 31 (unit will face a little left from the
    complete turn). Value of 32 means unit will face a random direction.

    유닛이 생성된 후 향하게 될 방향입니다. 값은 0(위쪽)에서 시작하여 이후 시계
    방향으로 31(위쪽에서 약간 왼쪽)까지 증가합니다. 값이 32이면 랜덤 방향을 향하게
    됩니다.
    """
    hasShield = ArrayMember(0x6647B0, Mk.BOOL)
    """bool: Flag indicating if the unit's shields are enabled.

    When enabled, the unit's shields can be modified with `ModifyUnitShields` action.
    Note that Terran and Zerg buildings under construction do not regenerate shields.

    활성화하면 `ModifyUnitShields` 액션으로 유닛의 보호막을 수정할 수 있습니다. 건설
    중인 테란 및 저그 건물은 보호막을 재생하지 않습니다.
    """
    maxShield = ArrayMember(0x660E00, Mk.WORD)
    "u16: Shield amount of unit. 유닛의 최대 실드량."
    maxHp = ArrayMember(0x662350, Mk.DWORD)
    """i32: Max hit point of unit.

    Values above '10000' are allowed in the game, but no numbers are displayed.

    유닛의 체력. '10000' 이상의 값은 게임에서 허용되지만 수치가 표시되지 않습니다.
    """
    elevation = ArrayMember(0x663150, Mk.BYTE)
    """u8: The unit's visible height.

    When set to Air (12 <= elevation <= 18), allows the unit to pass over impassable
    terrain or other ground units. The higher the value, sorts sprite elevation
    higher and appear above other units.

    유닛의 표시 높이. 공중으로 설정할 경우 (12 <= 높이 <= 18) 통과 불가 지형이나 다른
    지상 유닛 위로 지나다닐 수 있습니다. 값이 높을수록 지형이나 다른 유닛보다 위에
    표시됩니다.
    """
    movementFlags = MovementFlags(0x660FC8, Mk.BYTE)
    rank = ArrayMember(0x663DD0, Mk.RANK)
    """u16: Stat text id offset for unit rank, starting from [1302] Recruit.

    Sets the rank of the unit. Unit status text is prioritized in the following order
    (1) Hallucination (2) Buildings that are Disabled, Lockdown, Stasis, or Maelstrom
    (3) Acid Spores (4) Blind (5) Parasite (6) Detector (7) Rank. For a rank to be
    visible, it must have no `Building` and `SingleEntity` flags in `baseProperty`,
    and not be a Civilian or Spider Mine. Gantrithor, Battlecruiser, Norad II, and
    Hyperion must use their default names (`nameString` must be 0) to use the
    Tassadar/Admiral rank as fixed. Other units must only have `Terran` enabled in
    their race flags in `groupFlags` to see their ranks.

    유닛의 계급을 설정합니다. 유닛 상태 텍스트의 우선순위는 다음과 같습니다:
    (1) 할루시네이션 (2) 디시블, 락다운, 스테이시스, 마엘스트롬에 걸린 건물
    (3) 애시드 스포어 (4) 블라인드 (5) 패러사이트 (6) 디텍터 (7) 계급. 계급이
    보이려면 `baseProperty`에 `Building`과 `SingleEntity` 플래그가 없어야하고,
    시민이나 스파이더 마인이 아니어야 합니다. 간트리서, 배틀크루저, 노라드 II,
    히페리온은 기본 이름을 사용해야 (`nameString`이 0이어야) 태사다르/제독 계급을
    고정으로 사용합니다. 이 외의 유닛은 `groupFlags`의 종족 플래그에서 `Terran`만
    활성화해야 계급이 보입니다.
    """
    computerIdleOrder = ArrayMember(0x662EA0, Mk.UNIT_ORDER)
    """UnitOrder: An order issued when unit owned by computer is doing nothing.

    컴퓨터의 유닛이 아무것도 하고있지 않을 때 내려지는 명령.
    """
    humanIdleOrder = ArrayMember(0x662268, Mk.UNIT_ORDER)
    """UnitOrder: An order issued when unit owned by huamn is doing nothing

    사람의 유닛이 아무것도 하고있지 않을 때 내려지는 명령.
    """
    returnToIdleOrder = ArrayMember(0x664898, Mk.UNIT_ORDER)
    """UnitOrder: An order issued when unit return to idle state.

    유닛이 이전 명령을 수행한 후 아무것도 하지 않는 상태로 돌아가는 명령.
    """
    attackUnitOrder = ArrayMember(0x663320, Mk.UNIT_ORDER)
    """UnitOrder: An order performed when a unit is ordered to attack.

    Also performed by right-clicking if the target is an enemy.

    유닛이 대상을 공격하라고 명령 받았을 때 수행하는 명령. 대상이 적이면 우클릭으로도
    수행합니다.
    """
    attackMoveOrder = ArrayMember(0x663A50, Mk.UNIT_ORDER)
    groundWeapon = ArrayMember(0x6636B8, Mk.WEAPON)
    airWeapon = ArrayMember(0x6616E0, Mk.WEAPON)
    maxGroundHits = ArrayMember(0x6645E0, Mk.BYTE)
    """u8: (UNUSED) Maximum number of hits this unit can deal to ground targets.

    This attribute represents the maximum number of hits this unit can inflict on a
    target with its ground weapon. For example, the Psi Blades have a `damageFactor`
    of 1, while the Zealot has a `maxGroundHits` of 2. The actual number of attacks
    is determined by the iscript.

    유닛이 지상 무기로 대상을 타격할 수 있는 최대 명중 횟수입니다. 예를 들어,
    사이오닉 검의 `damageFactor`는 1이고 질럿의 `maxGroundHits`은 2입니다.
    실제 공격 횟수는 iscript에서 결정됩니다.
    """
    maxAirHits = ArrayMember(0x65FC18, Mk.BYTE)
    """u8: (UNUSED) Maximum number of hits this unit can deal to air targets.

    This attribute represents the maximum number of hits this unit can inflict on a
    target with its air weapon. For example, Halo Rockets have a `damageFactor` of 2,
    while the Valkyrie has a `maxAirHits` of 4. The actual number of attacks is
    determined by the iscript.

    유닛이 공중 무기로 대상을 타격할 수 있는 최대 명중 횟수입니다. 예를 들어, 광륜
    로켓의 `damageFactor`는 최대치인 2이고 발키리의 `maxAirHits`은 4입니다. 실제 공격
    횟수는 iscript에서 결정됩니다.
    """
    ignoreStrategicSuicideMissions = ArrayMember(0x660178, Mk.BOOL)
    """bool: Flag indicating if the unit is excluded from Strategic Suicide Missions.

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
    """bool: Flag to prevent unit from returning to original position.

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
    """
    baseProperty = BaseProperty(0x664080, Mk.DWORD)
    seekRange = ArrayMember(0x662DB8, Mk.BYTE)
    sightRange = ArrayMember(0x663238, Mk.BYTE)
    armorUpgrade = ArrayMember(0x6635D0, Mk.UPGRADE)
    sizeType = ArrayMember(0x662180, Mk.UNIT_SIZE)
    """u8: Size classification of the unit.

    Defines the size of unit as one of four types: `"Small"`, `"Medium"`, `"Large"`,
    or `"Independent"`. This size affects the damage calculation for various damage
    types. Damage multipliers for weapon damage types against each unit size are
    located at memory address `0x515B84`.

    유닛의 크기를 네 가지 타입 중 하나로 정의합니다: `"Small"`, `"Medium"`,
    `"Large"`, `"Independent"`. 방어 타입은 무기 타입에 따른 대미지 계산에 영향을
    줍니다. 각 무기 타입마다 방어 타입에 대한 대미지 비율은 메모리 주소 `0x515B84`에
    있습니다.
    """
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
    """Position: Dimensions for building placement and visibility.

    This dimension is used when determining if units with the Building flag can fit
    in the available spaace. Units without the Building flag will rely on their
    collision dimensions instead. Setting to 0x0 will make the unit invisible: It
    won't appear on screen and minimap, can't be selected by the mouse, and can't be
    targetted by other units. `Bring` condition will not locate it. Setting this to
    a size of 31x31 or smaller will allow buildings to be built on any terrain,
    including water and cliffs, although the placement mechanics are a little wonky.

    건물 플래그가 있는 유닛이 공간에 들어갈 수 있는지 여부를 결정할 때 사용됩니다.
    건물 플래그가 없는 유닛은 대신 유닛 크기에 의존합니다. 0x0으로 설정하면 유닛이
    보이지 않게 됩니다: 화면과 미니맵에 나타나지 않고 마우스로 선택할 수 없으며 다른
    유닛이 타겟팅할 수 없습니다. `Bring` 조건은 유닛을 찾지 못합니다. 이 크기를 31x31
    이하로 설정하면 배치 메커니즘이 약간 불안정하지만 물과 절벽을 포함한 모든 지형에
    건물을 지을 수 있습니다.
    """
    addonPlacement = NotImplementedMember(0x6626E0, Mk.POSITION)
    """AddonPlacement is not implemented yet because its beginning index isn't 0."""
    unitBoundsLT = ArrayMember(0x6617C8, Mk.POSITION, stride=8)
    unitBoundsRB = ArrayMember(0x6617CC, Mk.POSITION, stride=8)
    unitBoundsL = ArrayMember(0x6617C8, Mk.POSITION_X, stride=8)
    unitBoundsT = ArrayMember(0x6617CA, Mk.POSITION_Y, stride=8)
    unitBoundsR = ArrayMember(0x6617CC, Mk.POSITION_X, stride=8)
    unitBoundsB = ArrayMember(0x6617CE, Mk.POSITION_Y, stride=8)
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
    """TrgString: Map string id for the unit's name.

    When this property is non-zero, the unit's name is read from the strings in
    the currently loaded map (CHK) rather than from the `stat_txt.tbl` file.

    이 속성이 0이 아닌 경우, 유닛의 이름은 `stat_txt.tbl` 파일 대신 현재 로드된
    맵(CHK) 내의 문자열에서 읽어옵니다.
    """
    broodWarFlag = ArrayMember(0x6606D8, Mk.BYTE)  # bool?
    availabilityFlags = AvailabilityFlags(0x661518, Mk.WORD)

    @ut.classproperty
    def range(self):
        return (0, 227, 1)

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
