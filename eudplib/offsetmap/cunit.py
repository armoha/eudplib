#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TypeVar, cast

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.eudfunc.eudf import _EUDPredefineReturn
from ..localize import _
from .csprite import int_or_var
from .epdoffsetmap import EPDOffsetMap, epd_cache, ptr_cache
from .member import (
    CSpriteMember,
    CUnitMember,
    EnumMember,
    Flag,
    Member,
    MemberKind,
    PlayerDataMember,
    UnitDataMember,
    UnitOrderDataMember,
    UnsupportedMember,
)


class MovementFlags(EnumMember):
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


class StatusFlags(EnumMember):
    __slots__ = ()
    Completed = Flag(0x00000001)
    GroundedBuilding = Flag(0x00000002)  # a building that is on the ground
    InAir = Flag(0x00000004)
    Disabled = Flag(0x00000008)  # Protoss Unpowered
    Burrowed = Flag(0x00000010)
    InBuilding = Flag(0x00000020)
    InTransport = Flag(0x00000040)
    CanBeChased = Flag(0x00000080)
    RequiresDetection = Flag(0x00000100)
    Cloaked = Flag(0x00000200)
    DoodadStatesThing = Flag(
        0x00000400
    )  # protoss unpowered buildings have this flag set
    CloakingForFree = Flag(0x00000800)  # Requires no energy to cloak
    CanNotReceiveOrders = Flag(0x00001000)
    NoBrkCodeStart = Flag(0x00002000)  # Unbreakable code section in iscript
    UNKNOWN2 = Flag(0x00004000)
    CanNotAttack = Flag(0x00008000)
    CanTurnAroundToAttack = Flag(0x00010000)  # canAttack? named IsAUnit in BWAPI
    IsBuilding = Flag(0x00020000)
    IgnoreTileCollision = Flag(0x00040000)
    Unmovable = Flag(0x00080000)
    IsNormal = Flag(0x00100000)  # 1 for "normal" units, 0 for hallucinated units
    # if set, other units wont collide with the unit (like burrowed units)
    NoCollide = Flag(0x00200000)
    UNKNOWN5 = Flag(0x00400000)
    # if set, the unit wont collide with other units (like workers gathering)
    IsGathering = Flag(0x00800000)
    UNKNOWN6 = Flag(0x01000000)
    UNKNOWN7 = Flag(0x02000000)  # Turret related
    Invincible = Flag(0x04000000)
    # Set if the unit is currently holding position
    HoldingPosition = Flag(0x08000000)
    SpeedUpgrade = Flag(0x10000000)
    CooldownUpgrade = Flag(0x20000000)
    # 1 for hallucinated units, 0 for "normal" units
    IsHallucination = Flag(0x40000000)
    # Set for when the unit is self-destructing
    # (scarab, scourge, infested terran)
    IsSelfDestructing = Flag(0x80000000)


T = TypeVar("T", bound="CUnit")


# ruff: noqa: N815
class CUnit(EPDOffsetMap):
    __slots__ = "_ptr"
    # TODO: add docstring for descriptor
    prev = CUnitMember(0x000)
    get_next = CUnitMember(0x004)  # link
    # displayed value is ceil(healthPoints/256)
    hp = Member(0x008, MemberKind.DWORD)
    sprite = CSpriteMember(0x00C)
    moveTargetPos = Member(0x010, MemberKind.POSITION)
    moveTargetX = Member(0x010, MemberKind.POSITION_X)
    moveTargetY = Member(0x012, MemberKind.POSITION_Y)
    moveTarget = CUnitMember(0x014)
    moveTargetUnit = CUnitMember(0x014)
    # The next way point in the path the unit is following to get to
    # its destination. Equal to moveToPos for air units since they
    # don't need to navigate around buildings.
    nextMovementWaypoint = Member(0x018, MemberKind.POSITION)
    # The desired position
    nextTargetWaypoint = Member(0x01C, MemberKind.POSITION)
    movementFlags = MovementFlags(0x020, MemberKind.BYTE)
    # current direction the unit is facing
    currentDirection1 = Member(0x021, MemberKind.BYTE)
    turnRadius = Member(0x022, MemberKind.BYTE)  # flingy
    # usually only differs from the currentDirection field for units that
    # can accelerate and travel in a different direction than they are facing.
    # For example Mutalisks can change the direction they are facing
    # faster than then can change the direction they are moving.
    velocityDirection1 = Member(0x023, MemberKind.BYTE)
    flingyID = Member(0x024, MemberKind.FLINGY)
    unknown0x26 = Member(0x026, MemberKind.BYTE)
    flingyMovementType = Member(0x027, MemberKind.BYTE)
    # Current position of the unit
    pos = Member(0x028, MemberKind.POSITION)
    posX = Member(0x028, MemberKind.POSITION_X)
    posY = Member(0x02A, MemberKind.POSITION_Y)
    haltX = Member(0x02C, MemberKind.DWORD)
    haltY = Member(0x030, MemberKind.DWORD)
    topSpeed = Member(0x034, MemberKind.DWORD)
    currentSpeed1 = Member(0x038, MemberKind.DWORD)
    currentSpeed2 = Member(0x03C, MemberKind.DWORD)
    currentVelocityX = Member(0x040, MemberKind.DWORD)
    currentVelocityY = Member(0x044, MemberKind.DWORD)
    acceleration = Member(0x048, MemberKind.WORD)
    currentDirection2 = Member(0x04A, MemberKind.BYTE)
    velocityDirection2 = Member(0x04B, MemberKind.BYTE)  # pathing related
    playerID = PlayerDataMember(0x04C)
    owner = PlayerDataMember(0x04C)
    orderID = UnitOrderDataMember(0x04D)
    order = UnitOrderDataMember(0x04D)
    orderState = Member(0x04E, MemberKind.BYTE)
    orderSignal = Member(0x04F, MemberKind.BYTE)
    orderUnitType = UnitDataMember(0x050)
    unknown0x52 = Member(0x052, MemberKind.WORD)  # 2-byte padding
    cooldown = Member(0x054, MemberKind.DWORD)
    orderTimer = Member(0x054, MemberKind.BYTE)
    gCooldown = Member(0x055, MemberKind.BYTE)
    aCooldown = Member(0x056, MemberKind.BYTE)
    spellCooldown = Member(0x057, MemberKind.BYTE)
    groundWeaponCooldown = Member(0x055, MemberKind.BYTE)
    airWeaponCooldown = Member(0x056, MemberKind.BYTE)
    orderTargetPos = Member(0x058, MemberKind.POSITION)  # ActionFocus
    orderTargetXY = Member(0x058, MemberKind.POSITION)
    orderTargetX = Member(0x058, MemberKind.POSITION_X)
    orderTargetY = Member(0x05A, MemberKind.POSITION_Y)
    orderTarget = CUnitMember(0x05C)
    orderTargetUnit = CUnitMember(0x05C)
    shield = Member(0x060, MemberKind.DWORD)
    unitID = UnitDataMember(0x064)
    unitType = UnitDataMember(0x064)
    unknown0x66 = Member(0x066, MemberKind.WORD)  # 2-byte padding
    prevPlayerUnit = CUnitMember(0x068)
    nextPlayerUnit = CUnitMember(0x06C)
    subUnit = CUnitMember(0x070)
    orderQueueHead = UnsupportedMember(0x074, MemberKind.DWORD)  # COrder
    orderQueueTail = UnsupportedMember(0x078, MemberKind.DWORD)
    autoTargetUnit = CUnitMember(0x07C)
    # larva, in-transit, addons
    connectedUnit = CUnitMember(0x080)
    # may be count in addition to first since can be 2 when 3 orders are queued
    orderQueueCount = Member(0x084, MemberKind.BYTE)
    # Cycles down from from 8 to 0 (inclusive). See also 0x122.
    orderQueueTimer = Member(0x085, MemberKind.BYTE)
    unknown0x86 = Member(0x086, MemberKind.BYTE)
    # Prevent "Your forces are under attack." on every attack
    attackNotifyTimer = Member(0x087, MemberKind.BYTE)
    # zerg buildings while morphing
    prevUnitType = UnsupportedMember(0x088, MemberKind.UNIT)
    lastEventTimer = UnsupportedMember(0x08A, MemberKind.BYTE)
    # 17 = was completed (train, morph), 174 = was attacked
    lastEventColor = UnsupportedMember(0x08B, MemberKind.BYTE)
    #  might have originally been RGB from lastEventColor
    unknown0x8C = Member(0x08C, MemberKind.WORD)
    rankIncrease = Member(0x08E, MemberKind.BYTE)
    killCount = Member(0x08F, MemberKind.BYTE)
    lastAttackingPlayer = PlayerDataMember(0x090)
    secondaryOrderTimer = Member(0x091, MemberKind.BYTE)
    AIActionFlag = Member(0x092, MemberKind.BYTE)
    # 2 = issued an order
    # 3 = interrupted an order
    # 4 = hide self before death (self-destruct?)
    userActionFlags = Member(0x093, MemberKind.BYTE)
    currentButtonSet = Member(0x094, MemberKind.WORD)
    isCloaked = Member(0x096, MemberKind.BOOL)
    movementState = Member(0x097, MemberKind.BYTE)
    buildQueue1 = UnitDataMember(0x098)
    buildQueue2 = UnitDataMember(0x09A)
    buildQueue3 = UnitDataMember(0x09C)
    buildQueue4 = UnitDataMember(0x09E)
    buildQueue5 = UnitDataMember(0x0A0)
    buildQueue12 = Member(0x098, MemberKind.DWORD)
    buildQueue34 = Member(0x09C, MemberKind.DWORD)
    energy = Member(0x0A2, MemberKind.WORD)
    buildQueueSlot = Member(0x0A4, MemberKind.BYTE)
    targetOrderSpecial = Member(0x0A5, MemberKind.BYTE)
    uniquenessIdentifier = Member(0x0A5, MemberKind.BYTE)
    secondaryOrder = UnitOrderDataMember(0x0A6)
    secondaryOrderID = UnitOrderDataMember(0x0A6)
    # 0 means the building has the largest amount of fire/blood
    buildingOverlayState = Member(0x0A7, MemberKind.BYTE)
    hpGain = Member(0x0A8, MemberKind.WORD)  # buildRepairHpGain
    shieldGain = Member(0x0AA, MemberKind.WORD)  # Shield gain on construction
    # Remaining bulding time; also used by powerups (flags)
    # as the timer for returning to their original location.
    remainingBuildTime = Member(0x0AC, MemberKind.WORD)
    #  The HP of the unit before it changed
    # (example Drone->Hatchery, the Drone's HP will be stored here)
    prevHp = Member(0x0AE, MemberKind.WORD)
    # alphaID (StoredUnit)
    loadedUnit1 = UnsupportedMember(0x0B0, MemberKind.WORD)
    loadedUnit2 = UnsupportedMember(0x0B2, MemberKind.WORD)
    loadedUnit3 = UnsupportedMember(0x0B4, MemberKind.WORD)
    loadedUnit4 = UnsupportedMember(0x0B6, MemberKind.WORD)
    loadedUnit5 = UnsupportedMember(0x0B8, MemberKind.WORD)
    loadedUnit6 = UnsupportedMember(0x0BA, MemberKind.WORD)
    loadedUnit7 = UnsupportedMember(0x0BC, MemberKind.WORD)
    loadedUnit8 = UnsupportedMember(0x0BE, MemberKind.WORD)
    # union (0xC0 ~ 0xCF) //==================================
    spiderMineCount = Member(0x0C0, MemberKind.BYTE)  # vulture
    # carrier, reaver ----------------------------------------
    inHangarChild = CUnitMember(0x0C0)
    outHangarChild = CUnitMember(0x0C4)
    inHangarCount = Member(0x0C8, MemberKind.BYTE)
    outHangarCount = Member(0x0C9, MemberKind.BYTE)
    # interceptor, scarab ------------------------------------
    parent = CUnitMember(0x0C0)
    prevFighter = CUnitMember(0x0C4)
    nextFighter = CUnitMember(0x0C8)
    isOutsideHangar = Member(0x0CC, MemberKind.BOOL)
    # beacon -------------------------------------------------
    beaconUnknown0xC0 = Member(0x0C0, MemberKind.DWORD)
    beaconUnknown0xC4 = Member(0x0C4, MemberKind.DWORD)
    flagSpawnFrame = Member(0x0C8, MemberKind.DWORD)  # beacon
    # building /==============================================
    addon = CUnitMember(0x0C0)
    addonBuildType = UnitDataMember(0x0C4)
    upgradeResearchTime = Member(0x0C6, MemberKind.WORD)
    techType = Member(0x0C8, MemberKind.TECH)
    upgradeType = Member(0x0C9, MemberKind.UPGRADE)
    larvaTimer = Member(0x0CA, MemberKind.BYTE)
    landingTimer = Member(0x0CB, MemberKind.BYTE)
    creepTimer = Member(0x0CC, MemberKind.BYTE)
    upgradeLevel = Member(0x0CD, MemberKind.BYTE)
    # padding0xCE
    # resource -----------------------------------------------
    resourceAmount = Member(0x0D0, MemberKind.WORD)  # 0x0D0 union
    resourceIscript = Member(0x0D2, MemberKind.BYTE)
    gatherQueueCount = Member(0x0D3, MemberKind.BYTE)
    # pointer to the next worker unit waiting in line to gather
    nextGatherer = CUnitMember(0x0D4)
    resourceGroup = Member(0x0D8, MemberKind.BYTE)
    resourceBelongsToAI = Member(0x0D9, MemberKind.BYTE)
    # other buildings ----------------------------------------
    nydusExit = CUnitMember(0x0D0)  # connected nydus canal
    # confirmed to be CUnit* and not CSprite*
    ghostNukeMissile = Member(0x0D0, MemberKind.C_UNIT)
    pylonAura = Member(0x0D0, MemberKind.C_SPRITE)
    # silo
    siloNuke = CUnitMember(0x0D0)
    siloReady = Member(0x0D4, MemberKind.BOOL)
    # hatchery
    hatcheryHarvestL = Member(0x0D0, MemberKind.WORD)
    hatcheryHarvestU = Member(0x0D2, MemberKind.WORD)
    hatcheryHarvestR = Member(0x0D4, MemberKind.WORD)
    hatcheryHarvestB = Member(0x0D6, MemberKind.WORD)
    hatcheryHarvestLU = Member(0x0D0, MemberKind.DWORD)
    hatcheryHarvestRB = Member(0x0D4, MemberKind.DWORD)
    # ==============================================/ building
    # worker -------------------------------------------------
    powerup = CUnitMember(0x0C0)
    targetResourcePos = Member(0x0C4, MemberKind.POSITION)
    targetResourceX = Member(0x0C4, MemberKind.POSITION_X)
    targetResourceY = Member(0x0C6, MemberKind.POSITION_Y)
    targetResourceUnit = CUnitMember(0x0C8)
    repairResourceLossTimer = Member(0x0CC, MemberKind.WORD)
    isCarryingSomething = Member(0x0CE, MemberKind.BOOL)
    resourceCarryAmount = Member(0x0CF, MemberKind.BYTE)  # worker
    harvestTarget = CUnitMember(0x0D0)
    prevHarvestUnit = CUnitMember(0x0D4)
    nextHarvestUnit = CUnitMember(0x0D8)  # When there is a gather conflict
    # powerup ------------------------------------------------
    powerupOrigin = Member(0x0D0, MemberKind.POSITION)
    powerupOriginX = Member(0x0D0, MemberKind.POSITION_X)
    powerupOriginY = Member(0x0D2, MemberKind.POSITION_Y)  # powerup
    powerupCarryingUnit = CUnitMember(0x0D4)
    # \\\\\\\\\\\\\\\=================================// union
    statusFlags = StatusFlags(0x0DC, MemberKind.DWORD)
    # Type of resource chunk carried by this worker.
    # None = 0x00,
    # Vespene = 0x01,
    # Minerals = 0x02,
    # GasOrMineral = 0x03,
    # PowerUp = 0x04
    resourceType = Member(0x0E0, MemberKind.BYTE)
    wireframeRandomizer = Member(0x0E1, MemberKind.BYTE)
    secondaryOrderState = Member(0x0E2, MemberKind.BYTE)
    # Counts down from 15 to 0 when most orders are given,
    # or when the unit moves after reaching a patrol location
    recentOrderTimer = Member(0x0E3, MemberKind.BYTE)
    # which players can detect this unit (cloaked/burrowed)
    visibilityStatus = Member(0x0E4, MemberKind.DWORD)
    secondaryOrderPos = Member(0x0E8, MemberKind.POSITION)
    secondaryOrderX = Member(0x0E8, MemberKind.POSITION_X)
    secondaryOrderY = Member(0x0EA, MemberKind.POSITION_Y)
    currentBuildUnit = CUnitMember(0x0EC)
    prevBurrowedUnit = UnsupportedMember(0x0F0, MemberKind.C_UNIT)
    nextBurrowedUnit = UnsupportedMember(0x0F4, MemberKind.C_UNIT)
    rallyPos = Member(0x0F8, MemberKind.POSITION)
    rallyX = Member(0x0F8, MemberKind.POSITION_X)
    rallyY = Member(0x0FA, MemberKind.POSITION_Y)
    rallyUnit = CUnitMember(0x0FC)
    prevPsiProvider = CUnitMember(0x0F8)  # not supported?
    nextPsiProvider = CUnitMember(0x0FC)
    path = UnsupportedMember(0x100, MemberKind.DWORD)
    pathingCollisionInterval = Member(0x104, MemberKind.BYTE)
    # 0x01 = uses pathing; 0x02 = ?; 0x04 = ?
    pathingFlags = Member(0x105, MemberKind.BYTE)
    unknown0x106 = Member(0x106, MemberKind.BYTE)
    # 1 if a medic is currently healing this unit
    isBeingHealed = Member(0x107, MemberKind.BOOL)
    # A rect that specifies the closest contour (collision) points
    contourBoundsLU = UnsupportedMember(0x108, MemberKind.DWORD)
    contourBoundsL = UnsupportedMember(0x108, MemberKind.WORD)
    contourBoundsU = UnsupportedMember(0x10A, MemberKind.WORD)
    contourBoundsRB = UnsupportedMember(0x10C, MemberKind.DWORD)
    contourBoundsR = UnsupportedMember(0x10C, MemberKind.WORD)
    contourBoundsB = UnsupportedMember(0x10E, MemberKind.WORD)
    # Hallucination, Dark Swarm, Disruption Web, Broodling
    # (but not Scanner Sweep according to BWAPI)
    removeTimer = Member(0x110, MemberKind.WORD)
    defensiveMatrixHp = Member(0x112, MemberKind.WORD)
    defensiveMatrixTimer = Member(0x114, MemberKind.BYTE)
    stimTimer = Member(0x115, MemberKind.BYTE)
    ensnareTimer = Member(0x116, MemberKind.BYTE)
    lockdownTimer = Member(0x117, MemberKind.BYTE)
    irradiateTimer = Member(0x118, MemberKind.BYTE)
    stasisTimer = Member(0x119, MemberKind.BYTE)
    plagueTimer = Member(0x11A, MemberKind.BYTE)
    stormTimer = Member(0x11B, MemberKind.BYTE)
    # Used to tell if a unit is under psi storm	(is "stormTimer" in BWAPI)
    isUnderStorm = Member(0x11B, MemberKind.BYTE)
    irradiatedBy = CUnitMember(0x11C)
    irradiatePlayerID = PlayerDataMember(0x120)
    # Each bit corresponds to the player who has parasited this unit
    parasiteFlags = Member(0x121, MemberKind.BYTE)
    # counts/cycles up from 0 to 7 (inclusive). See also 0x85
    cycleCounter = Member(0x122, MemberKind.BYTE)
    # Each bit corresponds to the player who has optical flared this unit
    blindFlags = Member(0x123, MemberKind.BYTE)  # bool in BWAPI
    maelstromTimer = Member(0x124, MemberKind.BYTE)
    # Might be afterburner timer or ultralisk roar timer
    unusedTimer = Member(0x125, MemberKind.BYTE)
    acidSporeCount = Member(0x126, MemberKind.BYTE)
    acidSporeTime0 = Member(0x127, MemberKind.BYTE)
    acidSporeTime1 = Member(0x128, MemberKind.BYTE)
    acidSporeTime2 = Member(0x129, MemberKind.BYTE)
    acidSporeTime3 = Member(0x12A, MemberKind.BYTE)
    acidSporeTime4 = Member(0x12B, MemberKind.BYTE)
    acidSporeTime5 = Member(0x12C, MemberKind.BYTE)
    acidSporeTime6 = Member(0x12D, MemberKind.BYTE)
    acidSporeTime7 = Member(0x12E, MemberKind.BYTE)
    acidSporeTime8 = Member(0x12F, MemberKind.BYTE)
    # Cycles between 0-12 for each bullet fired by this unit
    # (if it uses a "Attack 3x3 area" weapon)
    offsetIndex3by3 = UnsupportedMember(0x130, MemberKind.WORD)
    unknown0x132 = UnsupportedMember(0x132, MemberKind.WORD)  # padding
    AI = UnsupportedMember(0x134, MemberKind.DWORD)
    airStrength = UnsupportedMember(0x138, MemberKind.WORD)
    groundStrength = UnsupportedMember(0x13A, MemberKind.WORD)
    finderIndexLeft = UnsupportedMember(0x13C, MemberKind.DWORD)
    finderIndexRight = UnsupportedMember(0x140, MemberKind.DWORD)
    finderIndexTop = UnsupportedMember(0x144, MemberKind.DWORD)
    finderIndexBottom = UnsupportedMember(0x148, MemberKind.DWORD)
    # updated only when air unit is being pushed
    repulseUnknown = Member(0x14C, MemberKind.BYTE)
    repulseAngle = Member(0x14D, MemberKind.BYTE)
    driftPos = Member(0x14E, MemberKind.WORD)  # (mapsizex / 1.5 max)
    driftX = Member(0x14E, MemberKind.BYTE)
    driftY = Member(0x14F, MemberKind.BYTE)

    def __init__(self, epd: int_or_var, *, ptr: int_or_var | None = None) -> None:
        """EPD Constructor of CUnit. Use CUnit.from_ptr(ptr) for ptr value"""
        _epd: int | c.EUDVariable
        self._ptr: int | c.EUDVariable | None

        if not isinstance(epd, CUnit):
            u, p = ut.unProxy(epd), ut.unProxy(ptr)
        else:
            u, p = epd._epd, epd._ptr
        if isinstance(u, int):
            if p is not None and not isinstance(p, int):
                raise ut.EPError(_("Invalid input for CUnit: {}").format((epd, ptr)))
            q, r = divmod(u - ut.EPD(0x59CCA8), 84)  # check epd
            if r == 0 and 0 <= q < 1700:
                _epd, self._ptr = u, 0x59CCA8 + 336 * q
            else:
                raise ut.EPError(_("Invalid input for CUnit: {}").format((epd, ptr)))
        elif isinstance(u, c.EUDVariable):
            if p is not None:
                if not isinstance(p, c.EUDVariable):
                    raise ut.EPError(
                        _("Invalid input for CUnit: {}").format((epd, ptr))
                    )
                _epd, self._ptr = c.EUDCreateVariables(2)
                c.SetVariables((_epd, self._ptr), (u, p))
            else:
                self._ptr = None
                _epd = c.EUDVariable()
                _epd << u
        else:
            raise ut.EPError(_("Invalid input for CUnit: {}").format((epd, ptr)))

        super().__init__(_epd)

    @classmethod
    def cast(cls: type[T], _from: int_or_var) -> T:
        return cls(_from)

    @classmethod
    def from_ptr(cls: type[T], ptr: int_or_var) -> T:
        epd: int | c.EUDVariable
        u = ut.unProxy(ptr)
        # check ptr
        if isinstance(u, int):
            q, r = divmod(u - 0x59CCA8, 336)
            if r == 0 and 0 <= q < 1700:
                epd = ut.EPD(u)
            else:
                raise ut.EPError(_("Invalid input for CUnit: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            epd = epd_cache(u)
        else:
            raise ut.EPError(_("Invalid input for CUnit: {}").format(epd))

        return cls(epd, ptr=u)

    @classmethod
    def from_read(cls: type[T], epd) -> T:
        from ..eudlib.memiof import f_cunitepdread_epd

        _ptr, _epd = f_cunitepdread_epd(epd)
        return cls(_epd, ptr=_ptr)

    @property
    def ptr(self) -> int | c.EUDVariable:
        if self._ptr is not None:
            return self._ptr
        return ptr_cache(cast(c.EUDVariable, self._epd))

    @staticmethod
    @c.EUDTypedFunc([None, None, c.TrgPlayer])
    def _cgive(unit, ptr, new_owner):
        from ..eudlib.memiof import f_dwwrite_epd

        unit = CUnit.cast(unit)
        if cs.EUDIf()(unit.order == 0):
            c.EUDReturn()
        cs.EUDEndIf()
        prev_owner = unit.owner
        unit.owner = new_owner
        new_header = ut.EPD(0x6283F8) + new_owner
        new_owner_65536 = new_owner << 16

        @c.EUDFunc
        def cgive_unit(ptr, epd):
            unit = CUnit.cast(epd)
            prv, nxt = unit.prevPlayerUnit, unit.nextPlayerUnit
            # no previous unit = unit is first unit of player
            if cs.EUDIf()(prv == 0):
                f_dwwrite_epd(ut.EPD(0x6283F8) + prev_owner, nxt.ptr)
            if cs.EUDElse()():
                # link next unit to previous unit
                prv.nextPlayerUnit = nxt
            cs.EUDEndIf()
            # link previous unit to next unit
            if cs.EUDIfNot()(nxt == 0):
                nxt.prevPlayerUnit = prv
            cs.EUDEndIf()

            if cs.EUDIf()(c.MemoryEPD(new_header, c.AtLeast, 0x59CCA8)):
                # get previous, next player units of recipient
                new_prev = CUnit.from_read(new_header)
                new_next = new_prev.nextPlayerUnit
                new_prev.nextPlayerUnit = ptr
                unit.prevPlayerUnit = new_prev
                unit.nextPlayerUnit = new_next
                if cs.EUDIfNot()(new_next == 0):
                    new_next.prevPlayerUnit = ptr
                cs.EUDEndIf()
            if cs.EUDElse()():
                f_dwwrite_epd(new_header, ptr)
                unit.prevPlayerUnit = 0
                unit.nextPlayerUnit = 0
            cs.EUDEndIf()

            # change sprite color of unit
            sprite = unit.sprite
            cs.DoActions(
                c.SetMemoryXEPD(
                    sprite + 0xA0 // 4, c.SetTo, new_owner_65536, 0xFF0000
                )
            )

        if cs.EUDIf()(unit.subUnit >= 0x59CCA8):
            subunit = unit.subUnit
            cgive_unit(subunit.ptr, subunit)
        cs.EUDEndIf()
        cgive_unit(ptr, unit)

    def cgive(self, player) -> None:
        CUnit._cgive(self, self.ptr, player)

    @staticmethod
    @c.EUDTypedFunc([None, c.TrgPlayer])
    def _set_color(unit, color_player65536):
        from ..eudlib.memiof import f_maskwrite_epd, f_spriteepdread_epd

        color_epd = c.EUDVariable()
        check_sprite = c.MemoryEPD(0, c.Exactly, 0)
        c.VProc(
            unit,
            [
                unit.AddNumber(0x0C // 4),
                unit.SetDest(ut.EPD(check_sprite) + 1),
            ],
        )
        if cs.EUDIfNot()(check_sprite):
            f_spriteepdread_epd(unit, ret=[ut.EPD(check_sprite) + 2, color_epd])
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
        return c.MemoryXEPD(self._epd + 0x0DC // 4, c.Exactly, value, mask)

    def set_status_flag(self, value, mask=None) -> None:
        from ..eudlib.memiof import f_maskwrite_epd

        if mask is None:
            mask = value
        f_maskwrite_epd(self._epd + 0x0DC // 4, value, mask)

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
    @c.EUDTypedFunc([None, c.TrgUnit])
    def _check_buildq(unit, unit_type):
        from ..eudlib import f_setcurpl2cpcache
        from ..trigger import Trigger

        ret = CUnit._check_buildq._frets[0]
        c.VProc(
            unit,
            [
                ret.SetNumber(0),
                c.SetMemory(0x6509B0, c.SetTo, 0x98 // 4),
                unit.QueueAddTo(ut.EPD(0x6509B0)),
            ],
        )
        Trigger(
            c.DeathsX(c.CurrentPlayer, c.Exactly, unit_type, 0, 0xFFFF),
            ret.SetNumber(1),
        )
        if cs.EUDIfNot()(ret == 1):
            unit65536 = unit_type * 65536  # Does not change CurrentPlayer
            Trigger(
                c.DeathsX(c.CurrentPlayer, c.Exactly, unit65536, 0, 0xFFFF0000),
                ret.SetNumber(1),
            )
            c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
            Trigger(
                c.DeathsX(c.CurrentPlayer, c.Exactly, unit_type, 0, 0xFFFF),
                ret.SetNumber(1),
            )
            Trigger(
                c.DeathsX(c.CurrentPlayer, c.Exactly, unit65536, 0, 0xFFFF0000),
                ret.SetNumber(1),
            )
            c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
            Trigger(
                c.DeathsX(c.CurrentPlayer, c.Exactly, unit_type, 0, 0xFFFF),
                ret.SetNumber(1),
            )
        cs.EUDEndIf()
        f_setcurpl2cpcache()
        # return False

    @staticmethod
    @_EUDPredefineReturn(1, 2)
    @c.EUDTypedFunc([None, c.TrgUnit, None])
    def _check_buildq_const(unit, unit_type, unit65536):
        from ..eudlib import f_setcurpl2cpcache
        from ..trigger import Trigger

        ret = CUnit._check_buildq_const._frets[0]
        c.VProc(
            unit,
            [
                ret.SetNumber(0),
                c.SetMemory(0x6509B0, c.SetTo, 0x98 // 4),
                unit.QueueAddTo(ut.EPD(0x6509B0)),
            ],
        )
        Trigger(
            c.DeathsX(c.CurrentPlayer, c.Exactly, unit_type, 0, 0xFFFF),
            ret.SetNumber(1),
        )
        Trigger(
            c.DeathsX(c.CurrentPlayer, c.Exactly, unit65536, 0, 0xFFFF0000),
            ret.SetNumber(1),
        )
        c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
        Trigger(
            c.DeathsX(c.CurrentPlayer, c.Exactly, unit_type, 0, 0xFFFF),
            ret.SetNumber(1),
        )
        Trigger(
            c.DeathsX(c.CurrentPlayer, c.Exactly, unit65536, 0, 0xFFFF0000),
            ret.SetNumber(1),
        )
        c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
        Trigger(
            c.DeathsX(c.CurrentPlayer, c.Exactly, unit_type, 0, 0xFFFF),
            ret.SetNumber(1),
        )
        f_setcurpl2cpcache()
        # return False

    @classmethod
    def from_next(cls: type[T]) -> "CUnit":
        return CUnit.from_read(ut.EPD(0x628438))

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
        self.set_status_flag(value=0x40000000, mask=0x40100000)

    def clear_hallucination(self) -> None:
        self.set_status_flag(value=0x00100000, mask=0x40100000)

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

        ut.ep_assert(not IsUnlimiterOn(), "Can't detect unit dying with [unlimiter]")
        # return (self.order == 0, self.sprite >= 1)
        return (
            c.MemoryXEPD(self._epd + 0x4D // 4, c.Exactly, 0, 0xFF00),
            c.MemoryEPD(self._epd + 0x0C // 4, c.AtLeast, 1),
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
        from ..eudlib import f_setloc_epd

        f_setloc_epd(location, self._epd + 0x28 // 4)

    def remove(self) -> None:
        self.userActionFlags = 4
        self.order = 0


EPDCUnitMap = CUnit
