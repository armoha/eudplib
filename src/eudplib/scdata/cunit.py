# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import Self, cast

from .. import core as c
from .. import ctrlstru as cs
from ..core.eudfunc.eudf import _EUDPredefineReturn
from ..localize import _
from ..utils import EPD, EPError, classproperty, unProxy
from .csprite import int_or_var
from .offsetmap import (
    EPDOffsetMap,
    Flag,
    StructEnumMember,
    StructMember,
    UnsupportedMember,
)
from .offsetmap import MemberKind as Mk
from .offsetmap.epdoffsetmap import _epd_cache, _ptr_cache
from .player import CurrentPlayer, TrgPlayer
from .unit import TrgUnit


class MovementFlags(StructEnumMember):
    """Flags that enable/disable certain movement."""

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


class StatusFlags(StructEnumMember):
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


class PathingFlags(StructEnumMember):
    __slots__ = ()
    HasCollision = Flag(0x01)
    IsStacked = Flag(0x02)
    Decollide = Flag(0x04)


class CUnit(EPDOffsetMap):
    __slots__ = ("_ptr",)
    prev = StructMember(0x000, Mk.C_UNIT)
    next = StructMember(0x004, Mk.C_UNIT)
    hp = StructMember(0x008, Mk.DWORD)
    "displayed value is ceil(healthPoints/256)"
    sprite = StructMember(0x00C, Mk.C_SPRITE)
    moveTargetPos = StructMember(0x010, Mk.POSITION)
    moveTargetX = StructMember(0x010, Mk.POSITION_X)
    moveTargetY = StructMember(0x012, Mk.POSITION_Y)
    moveTarget = moveTargetUnit = StructMember(0x014, Mk.C_UNIT)
    nextMovementWaypoint = StructMember(0x018, Mk.POSITION)
    """The next way point in the path the unit is following to get to its
    destination. Equal to moveToPos for air units since they don't need to
    navigate around buildings."""
    nextTargetWaypoint = StructMember(0x01C, Mk.POSITION)
    "The desired position"
    movementFlags = MovementFlags(0x020, Mk.BYTE)
    currentDirection1 = StructMember(0x021, Mk.BYTE)
    "current direction the unit is facing"
    turnSpeed = turnRadius = StructMember(0x022, Mk.BYTE)  # flingy
    velocityDirection1 = StructMember(0x023, Mk.BYTE)
    """usually only differs from the currentDirection field for units that
    can accelerate and travel in a different direction than they are facing.
    For example Mutalisks can change the direction they are facing
    faster than then can change the direction they are moving."""
    flingyID = StructMember(0x024, Mk.FLINGY)
    unknown0x26 = StructMember(0x026, Mk.BYTE)
    flingyMovementType = StructMember(0x027, Mk.BYTE)
    pos = StructMember(0x028, Mk.POSITION)
    "Current position of the unit"
    posX = StructMember(0x028, Mk.POSITION_X)
    posY = StructMember(0x02A, Mk.POSITION_Y)
    haltX = StructMember(0x02C, Mk.DWORD)
    haltY = StructMember(0x030, Mk.DWORD)
    topSpeed = StructMember(0x034, Mk.DWORD)
    currentSpeed1 = StructMember(0x038, Mk.DWORD)
    currentSpeed2 = StructMember(0x03C, Mk.DWORD)
    currentVelocityX = StructMember(0x040, Mk.DWORD)
    currentVelocityY = StructMember(0x044, Mk.DWORD)
    acceleration = StructMember(0x048, Mk.WORD)
    currentDirection2 = StructMember(0x04A, Mk.BYTE)
    velocityDirection2 = StructMember(0x04B, Mk.BYTE)
    "pathing related"
    owner = playerID = StructMember(0x04C, Mk.PLAYER)
    order = orderID = StructMember(0x04D, Mk.UNIT_ORDER)
    orderState = StructMember(0x04E, Mk.BYTE)
    orderSignal = StructMember(0x04F, Mk.BYTE)
    orderUnitType = StructMember(0x050, Mk.UNIT)
    unknown0x52 = StructMember(0x052, Mk.WORD)
    "2-byte padding"
    cooldown = StructMember(0x054, Mk.DWORD)
    orderTimer = StructMember(0x054, Mk.BYTE)
    groundWeaponCooldown = gCooldown = StructMember(0x055, Mk.BYTE)
    airWeaponCooldown = aCooldown = StructMember(0x056, Mk.BYTE)
    spellCooldown = StructMember(0x057, Mk.BYTE)
    # ActionFocus
    orderTargetXY = orderTargetPos = StructMember(0x058, Mk.POSITION)
    orderTargetX = StructMember(0x058, Mk.POSITION_X)
    orderTargetY = StructMember(0x05A, Mk.POSITION_Y)
    orderTarget = StructMember(0x05C, Mk.C_UNIT)
    orderTargetUnit = StructMember(0x05C, Mk.C_UNIT)
    shield = StructMember(0x060, Mk.DWORD)
    unitType = unitID = StructMember(0x064, Mk.UNIT)
    unknown0x66 = StructMember(0x066, Mk.WORD)
    "2-byte padding"
    prevPlayerUnit = StructMember(0x068, Mk.C_UNIT)
    nextPlayerUnit = StructMember(0x06C, Mk.C_UNIT)
    subUnit = StructMember(0x070, Mk.C_UNIT)
    orderQueueHead = UnsupportedMember(0x074, Mk.DWORD)  # COrder
    orderQueueTail = UnsupportedMember(0x078, Mk.DWORD)
    autoTargetUnit = StructMember(0x07C, Mk.C_UNIT)
    connectedUnit = StructMember(0x080, Mk.C_UNIT)
    "larva, in-transit, addons"
    orderQueueCount = StructMember(0x084, Mk.BYTE)
    "may be count in addition to first since can be 2 when 3 orders are queued"
    orderQueueTimer = StructMember(0x085, Mk.BYTE)
    "Cycles down from from 8 to 0 (inclusive). See also 0x122."
    unknown0x86 = StructMember(0x086, Mk.BYTE)
    attackNotifyTimer = StructMember(0x087, Mk.BYTE)
    "Prevent 'Your forces are under attack.' on every attack"
    prevUnitType = UnsupportedMember(0x088, Mk.UNIT)
    "zerg buildings while morphing"
    lastEventTimer = UnsupportedMember(0x08A, Mk.BYTE)
    lastEventColor = UnsupportedMember(0x08B, Mk.BYTE)
    "17 = was completed (train, morph), 174 = was attacked"
    unknown0x8C = StructMember(0x08C, Mk.WORD)
    "might have originally been RGB from lastEventColor"
    rankIncrease = StructMember(0x08E, Mk.RANK)
    killCount = StructMember(0x08F, Mk.BYTE)
    lastAttackingPlayer = StructMember(0x090, Mk.PLAYER)
    secondaryOrderTimer = StructMember(0x091, Mk.BYTE)
    AIActionFlag = StructMember(0x092, Mk.BYTE)
    userActionFlags = StructMember(0x093, Mk.BYTE)
    """2 = issued an order,
    3 = interrupted an order,
    4 = hide self before death (self-destruct?)"""
    currentButtonSet = StructMember(0x094, Mk.UNIT)
    isCloaked = StructMember(0x096, Mk.BOOL)
    movementState = StructMember(0x097, Mk.BYTE)
    buildQueue1 = StructMember(0x098, Mk.UNIT)
    buildQueue2 = StructMember(0x09A, Mk.UNIT)
    buildQueue3 = StructMember(0x09C, Mk.UNIT)
    buildQueue4 = StructMember(0x09E, Mk.UNIT)
    buildQueue5 = StructMember(0x0A0, Mk.UNIT)
    buildQueue12 = StructMember(0x098, Mk.DWORD)
    buildQueue34 = StructMember(0x09C, Mk.DWORD)
    energy = StructMember(0x0A2, Mk.WORD)
    buildQueueSlot = StructMember(0x0A4, Mk.BYTE)
    uniquenessIdentifier = targetOrderSpecial = StructMember(0x0A5, Mk.BYTE)
    secondaryOrder = secondaryOrderID = StructMember(0x0A6, Mk.UNIT_ORDER)
    buildingOverlayState = StructMember(0x0A7, Mk.BYTE)
    "0 means the building has the largest amount of fire/blood"
    hpGain = StructMember(0x0A8, Mk.WORD)
    "buildRepairHpGain"
    shieldGain = StructMember(0x0AA, Mk.WORD)
    "Shield gain on construction"
    remainingBuildTime = StructMember(0x0AC, Mk.WORD)
    """Remaining bulding time; also used by powerups (flags)
    as the timer for returning to their original location."""
    prevHp = StructMember(0x0AE, Mk.WORD)
    """The HP of the unit before it changed
    (example: Drone->Hatchery, the Drone's HP will be stored here)"""
    loadedUnit1 = UnsupportedMember(0x0B0, Mk.WORD)
    "alphaID (StoredUnit)"
    loadedUnit2 = UnsupportedMember(0x0B2, Mk.WORD)
    loadedUnit3 = UnsupportedMember(0x0B4, Mk.WORD)
    loadedUnit4 = UnsupportedMember(0x0B6, Mk.WORD)
    loadedUnit5 = UnsupportedMember(0x0B8, Mk.WORD)
    loadedUnit6 = UnsupportedMember(0x0BA, Mk.WORD)
    loadedUnit7 = UnsupportedMember(0x0BC, Mk.WORD)
    loadedUnit8 = UnsupportedMember(0x0BE, Mk.WORD)
    # union (0xC0 ~ 0xCF) //==================================
    spiderMineCount = StructMember(0x0C0, Mk.BYTE)  # vulture
    # carrier, reaver ----------------------------------------
    inHangarChild = StructMember(0x0C0, Mk.C_UNIT)
    outHangarChild = StructMember(0x0C4, Mk.C_UNIT)
    inHangarCount = StructMember(0x0C8, Mk.BYTE)
    outHangarCount = StructMember(0x0C9, Mk.BYTE)
    # interceptor, scarab ------------------------------------
    parent = StructMember(0x0C0, Mk.C_UNIT)
    prevFighter = StructMember(0x0C4, Mk.C_UNIT)
    nextFighter = StructMember(0x0C8, Mk.C_UNIT)
    isOutsideHangar = StructMember(0x0CC, Mk.BOOL)
    # beacon -------------------------------------------------
    beaconUnknown0xC0 = StructMember(0x0C0, Mk.DWORD)
    beaconUnknown0xC4 = StructMember(0x0C4, Mk.DWORD)
    flagSpawnFrame = StructMember(0x0C8, Mk.DWORD)  # beacon
    # building /==============================================
    addon = StructMember(0x0C0, Mk.C_UNIT)
    addonBuildType = StructMember(0x0C4, Mk.UNIT)
    upgradeResearchTime = StructMember(0x0C6, Mk.WORD)
    techType = StructMember(0x0C8, Mk.TECH)
    upgradeType = StructMember(0x0C9, Mk.UPGRADE)
    larvaTimer = StructMember(0x0CA, Mk.BYTE)
    landingTimer = StructMember(0x0CB, Mk.BYTE)
    creepTimer = StructMember(0x0CC, Mk.BYTE)
    upgradeLevel = StructMember(0x0CD, Mk.BYTE)
    # padding0xCE
    # resource -----------------------------------------------
    resourceAmount = StructMember(0x0D0, Mk.WORD)  # 0x0D0 union
    resourceIscript = StructMember(0x0D2, Mk.BYTE)
    gatherQueueCount = StructMember(0x0D3, Mk.BOOL)
    """it is byte but effectively bool; always set to 1 when beginning to harvest,
    but when finshed, it is    by 1 instead of set to 0"""
    nextGatherer = StructMember(0x0D4, Mk.C_UNIT)
    "pointer to the next worker unit waiting in line to gather"
    resourceGroup = StructMember(0x0D8, Mk.BYTE)
    resourceBelongsToAI = StructMember(0x0D9, Mk.BOOL)
    # other buildings ----------------------------------------
    nydusExit = StructMember(0x0D0, Mk.C_UNIT)
    "connected nydus canal"
    ghostNukeDot = StructMember(0x0D0, Mk.DWORD)  # FIXME: should be CThingy
    """CThingy struct is same as CUnit but trimmed down to [prev, next, hp, sprite],
    with "hp" field used as unitID for fog thingies or otherwise unused"""
    pylonAura = StructMember(0x0D0, Mk.C_SPRITE)
    # silo
    siloNuke = StructMember(0x0D0, Mk.C_UNIT)
    siloReady = StructMember(0x0D4, Mk.BOOL)
    # hatchery
    hatcheryHarvestLT = StructMember(0x0D0, Mk.DWORD)
    hatcheryHarvestRB = StructMember(0x0D4, Mk.DWORD)
    hatcheryHarvestL = StructMember(0x0D0, Mk.WORD)
    hatcheryHarvestT = StructMember(0x0D2, Mk.WORD)
    hatcheryHarvestR = StructMember(0x0D4, Mk.WORD)
    hatcheryHarvestB = StructMember(0x0D6, Mk.WORD)
    # ==============================================/ building
    # worker -------------------------------------------------
    powerup = StructMember(0x0C0, Mk.C_UNIT)
    targetResourcePos = StructMember(0x0C4, Mk.POSITION)
    targetResourceX = StructMember(0x0C4, Mk.POSITION_X)
    targetResourceY = StructMember(0x0C6, Mk.POSITION_Y)
    targetResourceUnit = StructMember(0x0C8, Mk.C_UNIT)
    repairResourceLossTimer = StructMember(0x0CC, Mk.WORD)
    isCarryingSomething = StructMember(0x0CE, Mk.BOOL)
    resourceCarryAmount = StructMember(0x0CF, Mk.BYTE)
    harvestTarget = StructMember(0x0D0, Mk.C_UNIT)
    prevHarvestUnit = StructMember(0x0D4, Mk.C_UNIT)
    nextHarvestUnit = StructMember(0x0D8, Mk.C_UNIT)
    "When there is a gather conflict"
    # powerup ------------------------------------------------
    powerupOrigin = StructMember(0x0D0, Mk.POSITION)
    powerupOriginX = StructMember(0x0D0, Mk.POSITION_X)
    powerupOriginY = StructMember(0x0D2, Mk.POSITION_Y)
    powerupCarryingUnit = StructMember(0x0D4, Mk.C_UNIT)
    # \\\\\\\\\\\\\\\=================================// union
    statusFlags = StatusFlags(0x0DC, Mk.DWORD)
    resourceType = StructMember(0x0E0, Mk.WORKER_CARRY_TYPE)
    "Type of resource chunk carried by worker: (None, Gas, Ore, GasOrOre, PowerUp)"
    wireframeRandomizer = StructMember(0x0E1, Mk.BYTE)
    secondaryOrderState = StructMember(0x0E2, Mk.BYTE)
    recentOrderTimer = StructMember(0x0E3, Mk.BYTE)
    """Counts down from 15 to 0 when most orders are given,
    or when the unit moves after reaching a patrol location"""
    visibilityStatus = StructMember(0x0E4, Mk.DWORD)
    "which players can detect this unit (cloaked/burrowed)"
    secondaryOrderPos = StructMember(0x0E8, Mk.POSITION)
    secondaryOrderX = StructMember(0x0E8, Mk.POSITION_X)
    secondaryOrderY = StructMember(0x0EA, Mk.POSITION_Y)
    currentBuildUnit = StructMember(0x0EC, Mk.C_UNIT)
    prevBurrowedUnit = UnsupportedMember(0x0F0, Mk.C_UNIT)
    nextBurrowedUnit = UnsupportedMember(0x0F4, Mk.C_UNIT)
    rallyPos = StructMember(0x0F8, Mk.POSITION)
    rallyX = StructMember(0x0F8, Mk.POSITION_X)
    rallyY = StructMember(0x0FA, Mk.POSITION_Y)
    rallyUnit = StructMember(0x0FC, Mk.C_UNIT)
    prevPsiProvider = StructMember(0x0F8, Mk.C_UNIT)
    nextPsiProvider = StructMember(0x0FC, Mk.C_UNIT)
    path = UnsupportedMember(0x100, Mk.DWORD)
    pathingCollisionInterval = StructMember(0x104, Mk.BYTE)
    pathingFlags = PathingFlags(0x105, Mk.BYTE)
    unknown0x106 = StructMember(0x106, Mk.BYTE)
    isBeingHealed = StructMember(0x107, Mk.BOOL)
    "1 if a medic is currently healing this unit"
    contourBoundsLT = UnsupportedMember(0x108, Mk.DWORD)
    "A rect that specifies the closest contour (collision) points"
    contourBoundsRB = UnsupportedMember(0x10C, Mk.DWORD)
    contourBoundsL = UnsupportedMember(0x108, Mk.WORD)
    contourBoundsT = UnsupportedMember(0x10A, Mk.WORD)
    contourBoundsR = UnsupportedMember(0x10C, Mk.WORD)
    contourBoundsB = UnsupportedMember(0x10E, Mk.WORD)
    removeTimer = StructMember(0x110, Mk.WORD)
    """Hallucination, Dark Swarm, Disruption Web, Broodling
    (but not Scanner Sweep according to BWAPI)"""
    defensiveMatrixHp = StructMember(0x112, Mk.WORD)
    defensiveMatrixTimer = StructMember(0x114, Mk.BYTE)
    stimTimer = StructMember(0x115, Mk.BYTE)
    ensnareTimer = StructMember(0x116, Mk.BYTE)
    lockdownTimer = StructMember(0x117, Mk.BYTE)
    irradiateTimer = StructMember(0x118, Mk.BYTE)
    stasisTimer = StructMember(0x119, Mk.BYTE)
    plagueTimer = StructMember(0x11A, Mk.BYTE)
    stormTimer = StructMember(0x11B, Mk.BYTE)
    isUnderStorm = StructMember(0x11B, Mk.BOOL)
    "Used to tell if a unit is under psi storm"
    irradiatedBy = StructMember(0x11C, Mk.C_UNIT)
    irradiatePlayerID = StructMember(0x120, Mk.PLAYER)
    parasiteFlags = StructMember(0x121, Mk.BYTE)
    "Each bit corresponds to the player who has parasited this unit"
    cycleCounter = StructMember(0x122, Mk.BYTE)
    "counts/cycles up from 0 to 7 (inclusive). See also 0x85"
    blindFlags = StructMember(0x123, Mk.BYTE)
    """Each bit corresponds to the player who has optical flared this unit,
    like parasiteFlags, but is read as a bool for vision check"""
    maelstromTimer = StructMember(0x124, Mk.BYTE)
    unusedTimer = StructMember(0x125, Mk.BYTE)
    "Might be afterburner timer or ultralisk roar timer"
    acidSporeCount = StructMember(0x126, Mk.BYTE)
    acidSporeTime0 = StructMember(0x127, Mk.BYTE)
    acidSporeTime1 = StructMember(0x128, Mk.BYTE)
    acidSporeTime2 = StructMember(0x129, Mk.BYTE)
    acidSporeTime3 = StructMember(0x12A, Mk.BYTE)
    acidSporeTime4 = StructMember(0x12B, Mk.BYTE)
    acidSporeTime5 = StructMember(0x12C, Mk.BYTE)
    acidSporeTime6 = StructMember(0x12D, Mk.BYTE)
    acidSporeTime7 = StructMember(0x12E, Mk.BYTE)
    acidSporeTime8 = StructMember(0x12F, Mk.BYTE)
    offsetIndex3by3 = UnsupportedMember(0x130, Mk.WORD)
    """Cycles between 0-12 for each bullet fired by this unit
    (if it uses a 'Attack 3x3 area' weapon)"""
    unknown0x132 = UnsupportedMember(0x132, Mk.WORD)
    "padding"
    AI = UnsupportedMember(0x134, Mk.DWORD)
    airStrength = UnsupportedMember(0x138, Mk.WORD)
    groundStrength = UnsupportedMember(0x13A, Mk.WORD)
    finderIndexLeft = UnsupportedMember(0x13C, Mk.DWORD)
    finderIndexRight = UnsupportedMember(0x140, Mk.DWORD)
    finderIndexTop = UnsupportedMember(0x144, Mk.DWORD)
    finderIndexBottom = UnsupportedMember(0x148, Mk.DWORD)
    repulseUnknown = StructMember(0x14C, Mk.BYTE)
    "updated only when air unit is being pushed"
    repulseAngle = StructMember(0x14D, Mk.BYTE)
    driftPos = StructMember(0x14E, Mk.WORD)
    "(mapsizex / 1.5 max)"
    driftX = StructMember(0x14E, Mk.BYTE)
    driftY = StructMember(0x14F, Mk.BYTE)

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
        self.buildQueue12 = 0xE40000 + q1
        self.buildQueue34 = 0xE400E4
        self.buildQueue5 = 0xE4

    def die(self) -> None:
        self.order = 0

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

    def set_noclip(self) -> None:
        self.set_status_flag(0x00100000)

    def clear_noclip(self) -> None:
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
        self.userActionFlags = 4
        self.order = 0


EPDCUnitMap = CUnit
