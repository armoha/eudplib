# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import ClassVar, Self, cast

from .. import core as c
from .. import ctrlstru as cs
from ..core.eudfunc.eudf import _EUDPredefineReturn
from ..localize import _
from ..utils import EPD, EPError, classproperty, unProxy
from .csprite import int_or_var
from .offsetmap import (
    BoolMember,
    ButtonSetMember,
    ByteEnum,
    ByteMember,
    CSpriteMember,
    CUnitMember,
    DwordEnum,
    DwordMember,
    EnumMember,
    EPDOffsetMap,
    Flag,
    FlingyMember,
    MovementFlags,
    PlayerMember,
    PositionMember,
    PositionXMember,
    PositionYMember,
    TechMember,
    UnitMember,
    UnitOrderMember,
    UnsupportedMember,
    UpgradeMember,
    WordMember,
    WorkerCarryTypeMember,
)
from .offsetmap.epdoffsetmap import _epd_cache, _ptr_cache
from .player import CurrentPlayer, TrgPlayer
from .unit import TrgUnit


class StatusFlags(EnumMember):
    __slots__ = ()
    Completed = Flag(0x00000001)
    GroundedBuilding = Flag(0x00000002)
    "a building that is on the ground"
    InAir = Flag(0x00000004)
    Disabled = Flag(0x00000008)
    "Protoss Unpowered"
    Burrowed = Flag(0x00000010)
    InBuilding = Flag(0x00000020)
    InTransport = Flag(0x00000040)
    CanBeChased = Flag(0x00000080)
    RequiresDetection = Flag(0x00000100)
    Cloaked = Flag(0x00000200)
    DoodadStatesThing = Flag(0x00000400)
    "protoss unpowered buildings have this flag set"
    CloakingForFree = Flag(0x00000800)
    "Requires no energy to cloak"
    CanNotReceiveOrders = Flag(0x00001000)
    NoBrkCodeStart = Flag(0x00002000)
    "Unbreakable code section in iscript"
    UNKNOWN2 = Flag(0x00004000)
    CanNotAttack = Flag(0x00008000)
    CanTurnAroundToAttack = Flag(0x00010000)
    "canAttack? named IsAUnit in BWAPI"
    IsBuilding = Flag(0x00020000)
    IgnoreTileCollision = Flag(0x00040000)
    Unmovable = Flag(0x00080000)
    IsNormal = Flag(0x00100000)
    "0 for ignore terrain elevation while moving"
    NoCollide = Flag(0x00200000)
    "if set, other units wont collide with the unit (like burrowed units)"
    UNKNOWN5 = Flag(0x00400000)
    IsGathering = Flag(0x00800000)
    "if set, the unit wont collide with other units (like workers gathering)"
    SubunitWalking = Flag(0x01000000)
    "makes subunit play walking animation if base unit movement flag 2 is set"
    SubunitFollow = Flag(0x02000000)
    "makes subunit instantly follow base unit's facing direction. Turret related"
    Invincible = Flag(0x04000000)
    HoldingPosition = Flag(0x08000000)
    "Set if the unit is currently holding position"
    SpeedUpgrade = Flag(0x10000000)
    CooldownUpgrade = Flag(0x20000000)
    IsHallucination = Flag(0x40000000)
    "1 for hallucinated units, 0 for 'normal' units"
    IsSelfDestructing = Flag(0x80000000)
    "Set for when the unit is self-destructing (scarab, scourge, infested terran)"


class PathingFlags(EnumMember):
    __slots__ = ()
    HasCollision = Flag(0x01)
    IsStacked = Flag(0x02)
    Decollide = Flag(0x04)


class CUnit(EPDOffsetMap):
    __slots__ = "_ptr"
    prev: ClassVar[CUnitMember] = CUnitMember("struct", 0x000)
    next: ClassVar[CUnitMember] = CUnitMember("struct", 0x004)
    hp: ClassVar[DwordMember] = DwordMember("struct", 0x008)
    "displayed value is ceil(healthPoints/256)"
    sprite: ClassVar[CSpriteMember] = CSpriteMember("struct", 0x00C)
    moveTargetPos: ClassVar[PositionMember] = PositionMember("struct", 0x010)
    moveTargetX: ClassVar[PositionXMember] = PositionXMember("struct", 0x010)
    moveTargetY: ClassVar[PositionYMember] = PositionYMember("struct", 0x012)
    moveTarget: ClassVar[CUnitMember] = CUnitMember("struct", 0x014)
    moveTargetUnit = moveTarget
    nextMovementWaypoint: ClassVar[PositionMember] = PositionMember("struct", 0x018)
    """The next way point in the path the unit is following to get to its
    destination. Equal to moveToPos for air units since they don't need to
    navigate around buildings."""
    nextTargetWaypoint: ClassVar[PositionMember] = PositionMember("struct", 0x01C)
    "The desired position"
    movementFlags = ByteEnum("struct", 0x020, MovementFlags)
    currentDirection1: ClassVar[ByteMember] = ByteMember("struct", 0x021)
    "current direction the unit is facing"
    turnSpeed: ClassVar[ByteMember] = ByteMember("struct", 0x022)  # flingy
    turnRadius = turnSpeed
    velocityDirection1: ClassVar[ByteMember] = ByteMember("struct", 0x023)
    """usually only differs from the currentDirection field for units that
    can accelerate and travel in a different direction than they are facing.
    For example Mutalisks can change the direction they are facing
    faster than then can change the direction they are moving."""
    flingyID: ClassVar[FlingyMember] = FlingyMember("struct", 0x024)
    unknown0x26: ClassVar[ByteMember] = ByteMember("struct", 0x026)
    flingyMovementType: ClassVar[ByteMember] = ByteMember("struct", 0x027)
    pos: ClassVar[PositionMember] = PositionMember("struct", 0x028)
    "Current position of the unit"
    posX: ClassVar[PositionXMember] = PositionXMember("struct", 0x028)
    posY: ClassVar[PositionYMember] = PositionYMember("struct", 0x02A)
    haltX: ClassVar[DwordMember] = DwordMember("struct", 0x02C)
    haltY: ClassVar[DwordMember] = DwordMember("struct", 0x030)
    topSpeed: ClassVar[DwordMember] = DwordMember("struct", 0x034)
    currentSpeed1: ClassVar[DwordMember] = DwordMember("struct", 0x038)
    currentSpeed2: ClassVar[DwordMember] = DwordMember("struct", 0x03C)
    currentVelocityX: ClassVar[DwordMember] = DwordMember("struct", 0x040)
    currentVelocityY: ClassVar[DwordMember] = DwordMember("struct", 0x044)
    acceleration: ClassVar[WordMember] = WordMember("struct", 0x048)
    currentDirection2: ClassVar[ByteMember] = ByteMember("struct", 0x04A)
    velocityDirection2: ClassVar[ByteMember] = ByteMember("struct", 0x04B)
    "pathing related"
    owner: ClassVar[PlayerMember] = PlayerMember("struct", 0x04C)
    playerID = owner
    order: ClassVar[UnitOrderMember] = UnitOrderMember("struct", 0x04D)
    orderID: ClassVar[UnitOrderMember] = UnitOrderMember("struct", 0x04D)
    orderState: ClassVar[ByteMember] = ByteMember("struct", 0x04E)
    orderSignal: ClassVar[ByteMember] = ByteMember("struct", 0x04F)
    orderUnitType: ClassVar[UnitMember] = UnitMember("struct", 0x050)
    unknown0x52: ClassVar[WordMember] = WordMember("struct", 0x052)
    "2-byte padding"
    cooldown: ClassVar[DwordMember] = DwordMember("struct", 0x054)
    orderTimer: ClassVar[ByteMember] = ByteMember("struct", 0x054)
    groundWeaponCooldown: ClassVar[ByteMember] = ByteMember("struct", 0x055)
    gCooldown = groundWeaponCooldown
    airWeaponCooldown: ClassVar[ByteMember] = ByteMember("struct", 0x056)
    aCooldown = airWeaponCooldown
    spellCooldown: ClassVar[ByteMember] = ByteMember("struct", 0x057)
    # ActionFocus
    orderTargetXY: ClassVar[PositionMember] = PositionMember("struct", 0x058)
    orderTargetPos = orderTargetXY
    orderTargetX: ClassVar[PositionXMember] = PositionXMember("struct", 0x058)
    orderTargetY: ClassVar[PositionYMember] = PositionYMember("struct", 0x05A)
    orderTarget: ClassVar[CUnitMember] = CUnitMember("struct", 0x05C)
    orderTargetUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x05C)
    shield: ClassVar[DwordMember] = DwordMember("struct", 0x060)
    unitType: ClassVar[UnitMember] = UnitMember("struct", 0x064)
    unitID = unitType
    unknown0x66: ClassVar[WordMember] = WordMember("struct", 0x066)
    "2-byte padding"
    prevPlayerUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x068)
    nextPlayerUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x06C)
    subUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x070)
    orderQueueHead: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x074)
    """COrder"""
    orderQueueTail: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x078)
    """COrder"""
    autoTargetUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x07C)
    connectedUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x080)
    "larva, in-transit, addons"
    orderQueueCount: ClassVar[ByteMember] = ByteMember("struct", 0x084)
    "may be count in addition to first since can be 2 when 3 orders are queued"
    orderQueueTimer: ClassVar[ByteMember] = ByteMember("struct", 0x085)
    "Cycles down from from 8 to 0 (inclusive). See also 0x122."
    unknown0x86: ClassVar[ByteMember] = ByteMember("struct", 0x086)
    attackNotifyTimer: ClassVar[ByteMember] = ByteMember("struct", 0x087)
    "Prevent 'Your forces are under attack.' on every attack"
    prevUnitType: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x088)
    "Unit. Zerg buildings while morphing"
    lastEventTimer: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x08A)
    """Byte"""
    lastEventColor: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x08B)
    "Byte. 17 = was completed (train, morph), 174 = was attacked"
    unknown0x8C: ClassVar[WordMember] = WordMember("struct", 0x08C)
    "might have originally been RGB from lastEventColor"
    rankIncrease: ClassVar[ByteMember] = ByteMember("struct", 0x08E)
    killCount: ClassVar[ByteMember] = ByteMember("struct", 0x08F)
    lastAttackingPlayer: ClassVar[PlayerMember] = PlayerMember("struct", 0x090)
    secondaryOrderTimer: ClassVar[ByteMember] = ByteMember("struct", 0x091)
    AIActionFlag: ClassVar[ByteMember] = ByteMember("struct", 0x092)
    userActionFlags: ClassVar[ByteMember] = ByteMember("struct", 0x093)
    """2 = issued an order,
    3 = interrupted an order,
    4 = hide self before death (self-destruct?)"""
    currentButtonSet: ClassVar[ButtonSetMember] = ButtonSetMember("struct", 0x094)
    isCloaked: ClassVar[BoolMember] = BoolMember("struct", 0x096)
    movementState: ClassVar[ByteMember] = ByteMember("struct", 0x097)
    buildQueue1: ClassVar[UnitMember] = UnitMember("struct", 0x098)
    buildQueue2: ClassVar[UnitMember] = UnitMember("struct", 0x09A)
    buildQueue3: ClassVar[UnitMember] = UnitMember("struct", 0x09C)
    buildQueue4: ClassVar[UnitMember] = UnitMember("struct", 0x09E)
    buildQueue5: ClassVar[UnitMember] = UnitMember("struct", 0x0A0)
    buildQueue12: ClassVar[DwordMember] = DwordMember("struct", 0x098)
    buildQueue34: ClassVar[DwordMember] = DwordMember("struct", 0x09C)
    energy: ClassVar[WordMember] = WordMember("struct", 0x0A2)
    buildQueueSlot: ClassVar[ByteMember] = ByteMember("struct", 0x0A4)
    uniquenessIdentifier: ClassVar[ByteMember] = ByteMember("struct", 0x0A5)
    targetOrderSpecial = uniquenessIdentifier
    secondaryOrder: ClassVar[UnitOrderMember] = UnitOrderMember("struct", 0x0A6)
    secondaryOrderID = secondaryOrder
    buildingOverlayState: ClassVar[ByteMember] = ByteMember("struct", 0x0A7)
    "0 means the building has the largest amount of fire/blood"
    hpGain: ClassVar[WordMember] = WordMember("struct", 0x0A8)
    "buildRepairHpGain"
    shieldGain: ClassVar[WordMember] = WordMember("struct", 0x0AA)
    "Shield gain on construction"
    remainingBuildTime: ClassVar[WordMember] = WordMember("struct", 0x0AC)
    """Remaining bulding time; also used by powerups (flags)
    as the timer for returning to their original location."""
    prevHp: ClassVar[WordMember] = WordMember("struct", 0x0AE)
    """The HP of the unit before it changed
    (example: Drone->Hatchery, the Drone's HP will be stored here)"""
    loadedUnit1: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0B0)
    "Word. alphaID (StoredUnit)"
    loadedUnit2: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0B2)
    "Word. alphaID (StoredUnit)"
    loadedUnit3: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0B4)
    "Word. alphaID (StoredUnit)"
    loadedUnit4: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0B6)
    "Word. alphaID (StoredUnit)"
    loadedUnit5: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0B8)
    "Word. alphaID (StoredUnit)"
    loadedUnit6: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0BA)
    "Word. alphaID (StoredUnit)"
    loadedUnit7: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0BC)
    "Word. alphaID (StoredUnit)"
    loadedUnit8: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x0BE)
    "Word. alphaID (StoredUnit)"
    # union (0xC0 ~ 0xCF) //==================================
    spiderMineCount: ClassVar[ByteMember] = ByteMember("struct", 0x0C0)  # vulture
    # carrier, reaver ----------------------------------------
    inHangarChild: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C0)
    outHangarChild: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C4)
    inHangarCount: ClassVar[ByteMember] = ByteMember("struct", 0x0C8)
    outHangarCount: ClassVar[ByteMember] = ByteMember("struct", 0x0C9)
    # interceptor, scarab ------------------------------------
    parent: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C0)
    prevFighter: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C4)
    nextFighter: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C8)
    isOutsideHangar: ClassVar[BoolMember] = BoolMember("struct", 0x0CC)
    # beacon -------------------------------------------------
    beaconUnknown0xC0: ClassVar[DwordMember] = DwordMember("struct", 0x0C0)
    beaconUnknown0xC4: ClassVar[DwordMember] = DwordMember("struct", 0x0C4)
    flagSpawnFrame: ClassVar[DwordMember] = DwordMember("struct", 0x0C8)  # beacon
    # building /==============================================
    addon: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C0)
    addonBuildType: ClassVar[UnitMember] = UnitMember("struct", 0x0C4)
    upgradeResearchTime: ClassVar[WordMember] = WordMember("struct", 0x0C6)
    techType: ClassVar[TechMember] = TechMember("struct", 0x0C8)
    upgradeType: ClassVar[UpgradeMember] = UpgradeMember("struct", 0x0C9)
    larvaTimer: ClassVar[ByteMember] = ByteMember("struct", 0x0CA)
    landingTimer: ClassVar[ByteMember] = ByteMember("struct", 0x0CB)
    creepTimer: ClassVar[ByteMember] = ByteMember("struct", 0x0CC)
    upgradeLevel: ClassVar[ByteMember] = ByteMember("struct", 0x0CD)
    # padding0xCE
    # resource -----------------------------------------------
    resourceAmount: ClassVar[WordMember] = WordMember("struct", 0x0D0)  # 0x0D0 union
    resourceIscript: ClassVar[ByteMember] = ByteMember("struct", 0x0D2)
    gatherQueueCount: ClassVar[BoolMember] = BoolMember("struct", 0x0D3)
    """it is byte but effectively bool; always set to 1 when beginning to harvest,
    but when finshed, it is    by 1 instead of set to 0"""
    nextGatherer: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D4)
    "pointer to the next worker unit waiting in line to gather"
    resourceGroup: ClassVar[ByteMember] = ByteMember("struct", 0x0D8)
    resourceBelongsToAI: ClassVar[BoolMember] = BoolMember("struct", 0x0D9)
    # other buildings ----------------------------------------
    nydusExit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D0)
    "connected nydus canal"
    # FIXME: should be CThingy
    ghostNukeDot: ClassVar[DwordMember] = DwordMember("struct", 0x0D0)
    """CThingy struct is same as CUnit but trimmed down to [prev, next, hp, sprite],
    with "hp" field used as unitID for fog thingies or otherwise unused"""
    pylonAura: ClassVar[CSpriteMember] = CSpriteMember("struct", 0x0D0)
    # silo
    siloNuke: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D0)
    siloReady: ClassVar[BoolMember] = BoolMember("struct", 0x0D4)
    # hatchery
    hatcheryHarvestLT: ClassVar[DwordMember] = DwordMember("struct", 0x0D0)
    hatcheryHarvestRB: ClassVar[DwordMember] = DwordMember("struct", 0x0D4)
    hatcheryHarvestL: ClassVar[WordMember] = WordMember("struct", 0x0D0)
    hatcheryHarvestT: ClassVar[WordMember] = WordMember("struct", 0x0D2)
    hatcheryHarvestR: ClassVar[WordMember] = WordMember("struct", 0x0D4)
    hatcheryHarvestB: ClassVar[WordMember] = WordMember("struct", 0x0D6)
    # ==============================================/ building
    # worker -------------------------------------------------
    powerup: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C0)
    targetResourcePos: ClassVar[PositionMember] = PositionMember("struct", 0x0C4)
    targetResourceX: ClassVar[PositionXMember] = PositionXMember("struct", 0x0C4)
    targetResourceY: ClassVar[PositionYMember] = PositionYMember("struct", 0x0C6)
    targetResourceUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0C8)
    repairResourceLossTimer: ClassVar[WordMember] = WordMember("struct", 0x0CC)
    isCarryingSomething: ClassVar[BoolMember] = BoolMember("struct", 0x0CE)
    resourceCarryAmount: ClassVar[ByteMember] = ByteMember("struct", 0x0CF)
    harvestTarget: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D0)
    prevHarvestUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D4)
    nextHarvestUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D8)
    "When there is a gather conflict"
    # powerup ------------------------------------------------
    powerupOrigin: ClassVar[PositionMember] = PositionMember("struct", 0x0D0)
    powerupOriginX: ClassVar[PositionXMember] = PositionXMember("struct", 0x0D0)
    powerupOriginY: ClassVar[PositionYMember] = PositionYMember("struct", 0x0D2)
    powerupCarryingUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0D4)
    # \\\\\\\\\\\\\\\=================================// union
    statusFlags = DwordEnum("struct", 0x0DC, StatusFlags)
    resourceType: ClassVar[WorkerCarryTypeMember] = WorkerCarryTypeMember(
        "struct", 0x0E0
    )
    "Type of resource chunk carried by worker: (None, Gas, Ore, GasOrOre, PowerUp)"
    wireframeRandomizer: ClassVar[ByteMember] = ByteMember("struct", 0x0E1)
    secondaryOrderState: ClassVar[ByteMember] = ByteMember("struct", 0x0E2)
    recentOrderTimer: ClassVar[ByteMember] = ByteMember("struct", 0x0E3)
    """Counts down from 15 to 0 when most orders are given,
    or when the unit moves after reaching a patrol location"""
    visibilityStatus: ClassVar[DwordMember] = DwordMember("struct", 0x0E4)
    "which players can detect this unit (cloaked/burrowed)"
    secondaryOrderPos: ClassVar[PositionMember] = PositionMember("struct", 0x0E8)
    secondaryOrderX: ClassVar[PositionXMember] = PositionXMember("struct", 0x0E8)
    secondaryOrderY: ClassVar[PositionYMember] = PositionYMember("struct", 0x0EA)
    currentBuildUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0EC)
    prevBurrowedUnit: ClassVar[UnsupportedMember] = UnsupportedMember(
        "struct", 0x0F0
    )  # CUnit
    nextBurrowedUnit: ClassVar[UnsupportedMember] = UnsupportedMember(
        "struct", 0x0F4
    )  # CUnit
    rallyPos: ClassVar[PositionMember] = PositionMember("struct", 0x0F8)
    rallyX: ClassVar[PositionXMember] = PositionXMember("struct", 0x0F8)
    rallyY: ClassVar[PositionYMember] = PositionYMember("struct", 0x0FA)
    rallyUnit: ClassVar[CUnitMember] = CUnitMember("struct", 0x0FC)
    prevPsiProvider: ClassVar[CUnitMember] = CUnitMember("struct", 0x0F8)
    nextPsiProvider: ClassVar[CUnitMember] = CUnitMember("struct", 0x0FC)
    path: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x100)  # Dword
    pathingCollisionInterval: ClassVar[ByteMember] = ByteMember("struct", 0x104)
    pathingFlags = ByteEnum("struct", 0x105, PathingFlags)
    unknown0x106: ClassVar[ByteMember] = ByteMember("struct", 0x106)
    isBeingHealed: ClassVar[BoolMember] = BoolMember("struct", 0x107)
    "1 if a medic is currently healing this unit"
    contourBoundsLT: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x108)
    """Dword"""
    "A rect that specifies the closest contour (collision) points"
    contourBoundsRB: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x10C)
    """Dword"""
    contourBoundsL: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x108)
    """Word"""
    contourBoundsT: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x10A)
    """Word"""
    contourBoundsR: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x10C)
    """Word"""
    contourBoundsB: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x10E)
    """Word"""
    removeTimer: ClassVar[WordMember] = WordMember("struct", 0x110)
    """Hallucination, Dark Swarm, Disruption Web, Broodling
    (but not Scanner Sweep according to BWAPI)"""
    defensiveMatrixHp: ClassVar[WordMember] = WordMember("struct", 0x112)
    defensiveMatrixTimer: ClassVar[ByteMember] = ByteMember("struct", 0x114)
    stimTimer: ClassVar[ByteMember] = ByteMember("struct", 0x115)
    ensnareTimer: ClassVar[ByteMember] = ByteMember("struct", 0x116)
    lockdownTimer: ClassVar[ByteMember] = ByteMember("struct", 0x117)
    irradiateTimer: ClassVar[ByteMember] = ByteMember("struct", 0x118)
    stasisTimer: ClassVar[ByteMember] = ByteMember("struct", 0x119)
    plagueTimer: ClassVar[ByteMember] = ByteMember("struct", 0x11A)
    stormTimer: ClassVar[ByteMember] = ByteMember("struct", 0x11B)
    isUnderStorm: ClassVar[BoolMember] = BoolMember("struct", 0x11B)
    "Used to tell if a unit is under psi storm"
    irradiatedBy: ClassVar[CUnitMember] = CUnitMember("struct", 0x11C)
    irradiatePlayerID: ClassVar[PlayerMember] = PlayerMember("struct", 0x120)
    parasiteFlags: ClassVar[ByteMember] = ByteMember("struct", 0x121)
    "Each bit corresponds to the player who has parasited this unit"
    cycleCounter: ClassVar[ByteMember] = ByteMember("struct", 0x122)
    "counts/cycles up from 0 to 7 (inclusive). See also 0x85"
    blindFlags: ClassVar[ByteMember] = ByteMember("struct", 0x123)
    """Each bit corresponds to the player who has optical flared this unit,
    like parasiteFlags, but is read as a bool for vision check"""
    maelstromTimer: ClassVar[ByteMember] = ByteMember("struct", 0x124)
    unusedTimer: ClassVar[ByteMember] = ByteMember("struct", 0x125)
    "Might be afterburner timer or ultralisk roar timer"
    acidSporeCount: ClassVar[ByteMember] = ByteMember("struct", 0x126)
    acidSporeTime0: ClassVar[ByteMember] = ByteMember("struct", 0x127)
    acidSporeTime1: ClassVar[ByteMember] = ByteMember("struct", 0x128)
    acidSporeTime2: ClassVar[ByteMember] = ByteMember("struct", 0x129)
    acidSporeTime3: ClassVar[ByteMember] = ByteMember("struct", 0x12A)
    acidSporeTime4: ClassVar[ByteMember] = ByteMember("struct", 0x12B)
    acidSporeTime5: ClassVar[ByteMember] = ByteMember("struct", 0x12C)
    acidSporeTime6: ClassVar[ByteMember] = ByteMember("struct", 0x12D)
    acidSporeTime7: ClassVar[ByteMember] = ByteMember("struct", 0x12E)
    acidSporeTime8: ClassVar[ByteMember] = ByteMember("struct", 0x12F)
    offsetIndex3by3: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x130)
    """Word"""
    """Cycles between 0-12 for each bullet fired by this unit
    (if it uses a 'Attack 3x3 area' weapon)"""
    unknown0x132: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x132)
    "Word. padding"
    AI: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x134)  # Dword
    airStrength: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x138)
    """Word"""
    groundStrength: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x13A)
    """Word"""
    finderIndexLeft: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x13C)
    """Dword"""
    finderIndexRight: ClassVar[UnsupportedMember] = UnsupportedMember(
        "struct", 0x140
    )  # Dword
    finderIndexTop: ClassVar[UnsupportedMember] = UnsupportedMember("struct", 0x144)
    """Dword"""
    finderIndexBottom: ClassVar[UnsupportedMember] = UnsupportedMember(
        "struct", 0x148
    )  # Dword
    repulseUnknown: ClassVar[ByteMember] = ByteMember("struct", 0x14C)
    "updated only when air unit is being pushed"
    repulseAngle: ClassVar[ByteMember] = ByteMember("struct", 0x14D)
    driftPos: ClassVar[WordMember] = WordMember("struct", 0x14E)
    "(mapsizex / 1.5 max)"
    driftX: ClassVar[ByteMember] = ByteMember("struct", 0x14E)
    driftY: ClassVar[ByteMember] = ByteMember("struct", 0x14F)

    @classproperty
    def range(self):
        return (EPD(0x59CCA8), EPD(0x59CCA8) + 84 * 1699, 84)

    def __init__(self, epd: int_or_var, *, ptr: int_or_var | None = None) -> None:
        """EPD Constructor of CUnit. Use CUnit.from_ptr(ptr) for ptr value"""
        _epd: int | c.EUDVariable
        self._ptr: int | c.EUDVariable | None

        if not isinstance(epd, CUnit):
            u, p = unProxy(epd), unProxy(ptr)
        else:
            u, p = epd._value, epd._ptr

        if isinstance(u, int):
            q, r = divmod(u - EPD(0x59CCA8), 84)  # check epd
            if r == 0 and 0 <= q < 1700:
                _epd, self._ptr = u, 0x59CCA8 + 336 * q
            else:
                raise EPError(_("Invalid input for CUnit: {}").format(epd))

            if p is not None and (not isinstance(p, int) or p != self._ptr):
                raise EPError(_("Invalid input for CUnit.ptr: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            if p is None:
                self._ptr = None
                if EPDOffsetMap._cast:
                    _epd = u
                else:
                    _epd = c.EUDVariable()
                    _epd << u
            else:
                if not isinstance(p, c.EUDVariable):
                    raise EPError(_("Invalid input for CUnit.ptr: {}").format(ptr))
                if EPDOffsetMap._cast:
                    _epd, self._ptr = u, p
                else:
                    _epd, self._ptr = c.EUDCreateVariables(2)
                    c.SetVariables((_epd, self._ptr), (u, p))
        else:
            raise EPError(_("Invalid input for CUnit: {}").format(epd))

        EPDOffsetMap._cast = False
        super().__init__(_epd)

    @classmethod
    def from_ptr(cls, ptr: int_or_var) -> Self:
        epd: int | c.EUDVariable
        u = unProxy(ptr)
        # check ptr
        if isinstance(u, int):
            q, r = divmod(u - 0x59CCA8, 336)
            if r == 0 and 0 <= q < 1700:
                epd = EPD(u)
            else:
                raise EPError(_("Invalid input for CUnit: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            epd = _epd_cache(u)
        else:
            raise EPError(_("Invalid input for CUnit: {}").format(epd))

        return cls(epd, ptr=u)

    @classmethod
    def from_read(cls, epd) -> Self:
        from ..memio import f_cunitepdread_epd

        _ptr, _epd = f_cunitepdread_epd(epd)
        return cls(_epd, ptr=_ptr)

    @classmethod
    def from_next(cls) -> Self:
        return cls.from_read(EPD(0x628438))

    @property
    def ptr(self) -> int | c.EUDVariable:
        if isinstance(self._value, int):
            return cast(int, self._ptr)  # FIXME
        if self._ptr is None:
            self._ptr = c.EUDVariable()
        return _ptr_cache(self._value, self._ptr)

    @staticmethod
    @c.EUDTypedFunc([None, None, TrgPlayer])
    def _cgive(unit, ptr, new_owner):
        from ..memio import f_cunitepdread_epd, f_dwwrite_epd, f_maskread_epd

        unit += 0x4C // 4  # playerID, orderID
        if cs.EUDIf()(c.MemoryXEPD(unit, c.Exactly, 0, 0xFF00)):
            c.EUDReturn()
        cs.EUDEndIf()

        prev_owner = f_maskread_epd(unit, 0xF)
        cs.DoActions(c.SetMemoryXEPD(unit, c.SetTo, new_owner, 0xFF))
        unit += 0x68 // 4 - 0x4C // 4  # prevPlayerUnit
        prev_ptr, prev_epd = f_cunitepdread_epd(unit)
        c.SetVariables(  # nextPlayerUnit
            [unit, prev_epd, prev_owner, new_owner],  # new_header
            [0x6C // 4 - 0x68 // 4, 0x6C // 4, EPD(0x6283F8), EPD(0x6283F8)],
            [c.Add, c.Add, c.Add, c.Add],
        )
        next_ptr, next_epd = f_cunitepdread_epd(unit)

        if cs.EUDIf()(prev_ptr >= 0x59CCA8):
            f_dwwrite_epd(prev_epd, next_ptr)
        if cs.EUDElse()():
            f_dwwrite_epd(EPD(0x6283F8) + prev_owner, next_ptr)
        cs.EUDEndIf()

        if cs.EUDIf()(next_ptr >= 0x59CCA8):
            next_epd += 0x68 // 4
            f_dwwrite_epd(next_epd, prev_ptr)
        cs.EUDEndIf()

        if cs.EUDIf()(c.MemoryEPD(new_owner, c.AtLeast, 0x59CCA8)):
            newprev_ptr, newprev_epd = f_cunitepdread_epd(new_owner)
            newprev_epd += 0x6C // 4
            newnext_ptr, newnext_epd = f_cunitepdread_epd(newprev_epd)
            f_dwwrite_epd(newprev_epd, ptr)
            f_dwwrite_epd(unit, newnext_ptr)
            unit -= 0x6C // 4 - 0x68 // 4  # prevPlayerUnit
            f_dwwrite_epd(unit, newprev_ptr)
            if cs.EUDIf()(newnext_ptr >= 0x59CCA8):
                newnext_epd += 0x68 // 4
                f_dwwrite_epd(newnext_epd, ptr)
            cs.EUDEndIf()
        if cs.EUDElse()():
            f_dwwrite_epd(new_owner, ptr)
            f_dwwrite_epd(unit, 0)
            unit -= 0x6C // 4 - 0x68 // 4  # prevPlayerUnit
            f_dwwrite_epd(unit, 0)
        cs.EUDEndIf()

    @staticmethod
    @c.EUDTypedFunc([None, None, TrgPlayer, None])
    def _cgive_subunit(unit, ptr, new_owner, ignore_subunit):
        from ..memio import f_cunitepdread_epd

        CUnit._cgive(unit, ptr, new_owner)
        unit += 0x70 // 4  # subunit
        if cs.EUDIf()([c.MemoryEPD(unit, c.AtLeast, 0x59CCA8), ignore_subunit == 0]):
            subunit_ptr, subunit = f_cunitepdread_epd(unit)
            CUnit._cgive(subunit, subunit_ptr, new_owner)
        cs.EUDEndIf()

    def cgive(self, new_owner, *, ignore_subunit=False) -> None:
        if ignore_subunit:
            CUnit._cgive_subunit(self, self.ptr, new_owner, ignore_subunit)
        else:
            CUnit._cgive(self, self.ptr, new_owner)

    @staticmethod
    @c.EUDTypedFunc([None, TrgPlayer])
    def _set_color(unit, color_player65536):
        from ..memio import f_maskwrite_epd, f_spriteepdread_epd

        color_epd = c.EUDVariable()
        check_sprite = c.MemoryEPD(0, c.Exactly, 0)
        c.VProc(
            unit,
            [
                unit.AddNumber(0x0C // 4),
                unit.SetDest(EPD(check_sprite) + 1),
            ],
        )
        if cs.EUDIfNot()(check_sprite):
            f_spriteepdread_epd(unit, ret=[EPD(check_sprite) + 2, color_epd])
        cs.EUDEndIf()
        if cs.EUDIfNot()(color_epd <= 2):
            f_maskwrite_epd(color_epd + 2, color_player65536, 0xFF0000)
        cs.EUDEndIf()

    def set_color(self, color_player) -> None:
        color_player = c.EncodePlayer(color_player)
        CUnit._set_color(self, color_player * 65536)

    def check_status_flag(self, value, mask=None) -> c.Condition:
        if mask is None:
            mask = value
        return c.MemoryXEPD(self._value + 0x0DC // 4, c.Exactly, value, mask)

    def set_status_flag(self, value, mask=None) -> None:
        from ..memio import f_maskwrite_epd

        if mask is None:
            mask = value
        f_maskwrite_epd(self._value + 0x0DC // 4, value, mask)

    def clear_status_flag(self, mask) -> None:
        self.set_status_flag(0, mask)

    def are_buildq_empty(self) -> list[c.Condition]:
        return [
            self.eqattr("buildQueue12", 0xE400E4),
            self.eqattr("buildQueue34", 0xE400E4),
            self.eqattr("buildQueue5", 0xE4),
        ]

    @staticmethod
    @_EUDPredefineReturn(2, 3)
    @c.EUDTypedFunc([None, TrgUnit])
    def _check_buildq(unit, unit_type):
        from ..memio import f_setcurpl2cpcache

        ret = CUnit._check_buildq._frets[0]

        check_bq0 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF)
        c.VProc(
            [unit, unit_type],
            [
                ret.SetNumber(0),
                c.SetMemory(0x6509B0, c.SetTo, 0x98 // 4),
                unit.QueueAddTo(EPD(0x6509B0)),
                unit_type.SetDest(EPD(check_bq0) + 2),
            ],
        )
        c.RawTrigger(conditions=check_bq0, actions=ret.SetNumber(1))
        if cs.EUDIfNot()(ret == 1):
            check_bq1 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF0000)
            check_bq2 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF)
            unit65536 = unit_type * 65536  # Does not change CurrentPlayer
            c.VProc(
                [unit65536, unit_type],
                [
                    unit65536.SetDest(EPD(check_bq1) + 2),
                    unit_type.SetDest(EPD(check_bq2) + 2),
                ],
            )
            c.RawTrigger(conditions=check_bq1, actions=ret.SetNumber(1))

            check_bq3 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF0000)
            check_bq4 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF)
            c.VProc(
                [unit65536, unit_type],
                [
                    c.SetMemory(0x6509B0, c.Add, 1),
                    unit65536.SetDest(EPD(check_bq3) + 2),
                    unit_type.SetDest(EPD(check_bq4) + 2),
                ],
            )
            c.RawTrigger(conditions=check_bq2, actions=ret.SetNumber(1))
            c.RawTrigger(conditions=check_bq3, actions=ret.SetNumber(1))
            c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
            c.RawTrigger(conditions=check_bq4, actions=ret.SetNumber(1))
        cs.EUDEndIf()
        f_setcurpl2cpcache()
        # return False

    @staticmethod
    @_EUDPredefineReturn(1, 2)
    @c.EUDTypedFunc([None, TrgUnit, None])
    def _check_buildq_const(unit, unit_type, unit65536):
        from ..memio import f_setcurpl2cpcache

        ret = CUnit._check_buildq_const._frets[0]

        check_bq0 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF)
        check_bq1 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF0000)
        c.VProc(
            [unit, unit_type, unit65536],
            [
                ret.SetNumber(0),
                c.SetMemory(0x6509B0, c.SetTo, 0x98 // 4),
                unit.QueueAddTo(EPD(0x6509B0)),
                unit_type.SetDest(EPD(check_bq0) + 2),
                unit65536.SetDest(EPD(check_bq1) + 2),
            ],
        )
        c.RawTrigger(conditions=check_bq0, actions=ret.SetNumber(1))
        c.RawTrigger(conditions=check_bq1, actions=ret.SetNumber(1))

        check_bq2 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF)
        check_bq3 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF0000)
        c.VProc(
            [unit_type, unit65536],
            [
                c.SetMemory(0x6509B0, c.Add, 1),
                unit_type.SetDest(EPD(check_bq2) + 2),
                unit65536.SetDest(EPD(check_bq3) + 2),
            ],
        )
        c.RawTrigger(conditions=check_bq2, actions=ret.SetNumber(1))
        c.RawTrigger(conditions=check_bq3, actions=ret.SetNumber(1))

        check_bq4 = c.DeathsX(CurrentPlayer, c.Exactly, 0, 0, 0xFFFF)
        c.VProc(
            unit_type,
            [c.SetMemory(0x6509B0, c.Add, 1), unit_type.SetDest(EPD(check_bq4) + 2)],
        )
        c.RawTrigger(conditions=check_bq4, actions=ret.SetNumber(1))
        f_setcurpl2cpcache()
        # return False

    def check_buildq(self, unit_type) -> c.Condition:
        unit = c.EncodeUnit(unit_type)
        if isinstance(unit, int):
            return CUnit._check_buildq_const(self, unit, unit * 65536)
        else:
            return CUnit._check_buildq(self, unit)

    def reset_buildq(self, q1=0xE4) -> None:
        # See https://github.com/python/mypy/issues/14969
        self.buildQueue12 = 0xE40000 + q1  # type: ignore[misc]
        self.buildQueue34 = 0xE400E4  # type: ignore[misc]
        self.buildQueue5 = 0xE4  # type: ignore[misc]

    def die(self) -> None:
        # See https://github.com/python/mypy/issues/14969
        self.order = 0  # type: ignore[misc]

    def remove_collision(self) -> None:
        self.set_status_flag(0x00A00000)

    def set_collision(self) -> None:
        self.clear_status_flag(0x00A00000)

    def set_invincible(self) -> None:
        self.set_status_flag(0x04000000)

    def clear_invincible(self) -> None:
        self.clear_status_flag(0x04000000)

    def set_gathering(self) -> None:
        self.set_status_flag(0x00800000)

    def clear_gathering(self) -> None:
        self.clear_status_flag(0x00800000)

    def set_speed_upgrade(self) -> None:
        self.set_status_flag(0x10000000)

    def clear_speed_upgrade(self) -> None:
        self.clear_status_flag(0x10000000)

    def set_hallucination(self) -> None:
        self.set_status_flag(0x40000000)

    def clear_hallucination(self) -> None:
        self.clear_status_flag(0x40000000)

    def power(self) -> None:
        self.clear_status_flag(0x00000008)

    def unpower(self) -> None:
        self.set_status_flag(0x00000008)

    def set_air(self) -> None:
        self.set_status_flag(0x00000004)

    def set_ground(self) -> None:
        self.clear_status_flag(0x00000004)

    def clear_noclip(self) -> None:
        self.set_status_flag(0x00100000)

    def set_noclip(self) -> None:
        self.clear_status_flag(0x00100000)

    def is_dying(self) -> tuple[c.Condition, c.Condition]:
        from ..eudlib.utilf.unlimiterflag import IsUnlimiterOn

        if IsUnlimiterOn():
            raise EPError(_("Can't detect unit dying with [unlimiter]"))
        return (  # return (self.order == 0, self.sprite >= 1)
            c.MemoryXEPD(self._value + 0x4D // 4, c.Exactly, 0, 0xFF00),
            c.MemoryEPD(self._value + 0x0C // 4, c.AtLeast, 1),
        )

    def is_completed(self) -> c.Condition:
        return self.check_status_flag(0x00000001)

    def is_hallucination(self) -> c.Condition:
        return self.check_status_flag(0x40000000)

    def is_air(self):
        return self.check_status_flag(0x00000004)

    def is_in_building(self) -> c.Condition:
        return self.check_status_flag(0x00000020)

    def is_in_transport(self) -> c.Condition:
        return self.check_status_flag(0x00000040)

    def is_burrowed(self) -> c.Condition:
        return self.check_status_flag(0x00000010)

    def setloc(self, location) -> None:
        from ..eudlib.locf.locf import f_setloc_epd

        f_setloc_epd(location, self._value + 0x28 // 4)

    def remove(self) -> None:
        # See https://github.com/python/mypy/issues/14969
        self.userActionFlags = 4  # type: ignore[misc]
        self.order = 0  # type: ignore[misc]


EPDCUnitMap = CUnit
