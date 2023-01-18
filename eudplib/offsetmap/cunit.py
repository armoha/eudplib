#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Mapping
from typing import cast, ClassVar, TypeVar

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from ..eudlib.locf import f_setloc_epd
from ..eudlib.memiof import (
    f_bwrite_epd,
    f_cunitepdread_epd,
    f_maskwrite_epd,
    f_spriteepdread_epd,
)
from ..eudlib.utilf.unlimiterflag import IsUnlimiterOn
from .epdoffsetmap import (
    CUnitMember,
    CSpriteMember,
    MemberKind,
    Member,
    EPDOffsetMap,
    UnsupportedMember,
    EPDCache,
    PtrCache,
    int_or_var,
)

T = TypeVar("T", bound="CUnit")


class CUnit(EPDOffsetMap):
    __slots__ = "_ptr"

    # TODO: add docstring for descriptor
    prev = CUnitMember(0x000)
    next = CUnitMember(0x004)  # link
    # displayed value is ceil(healthPoints/256)
    hp = Member(0x008, MemberKind.DWORD)
    sprite = CSpriteMember(0x00C)
    moveTargetPos = Member(0x010, MemberKind.POSITION)
    moveTargetX = Member(0x010, MemberKind.POSITION_X)
    moveTargetY = Member(0x012, MemberKind.POSITION_Y)
    moveTarget = CUnitMember(0x014)
    moveTargetUnit = CUnitMember(0x014)
    # The next way point in the path the unit is following to get to its destination.
    # Equal to moveToPos for air units since they don't need to navigate around buildings.
    nextMovementWaypoint = Member(0x018, MemberKind.POSITION)
    # The desired position
    nextTargetWaypoint = Member(0x01C, MemberKind.POSITION)
    movementFlags = Member(0x020, MemberKind.BYTE)
    # current direction the unit is facing
    direction = Member(0x021, MemberKind.BYTE)
    currentDirection1 = Member(0x021, MemberKind.BYTE)
    flingyTurnRadius = Member(0x022, MemberKind.BYTE)
    # usually only differs from the currentDirection field for units that can accelerate
    # and travel in a different direction than they are facing. For example Mutalisks can change
    # the direction they are facing faster than then can change the direction they are moving.
    velocityDirection1 = Member(0x023, MemberKind.BYTE)
    flingyID = Member(0x024, MemberKind.FLINGY)
    _unknown_0x026 = Member(0x026, MemberKind.BYTE)
    flingyMovementType = Member(0x027, MemberKind.BYTE)
    # Current position of the unit
    pos = Member(0x028, MemberKind.POSITION)
    posX = Member(0x028, MemberKind.POSITION_X)
    posY = Member(0x02A, MemberKind.POSITION_Y)
    position = Member(0x028, MemberKind.POSITION)
    positionX = Member(0x028, MemberKind.POSITION_X)
    positionY = Member(0x02A, MemberKind.POSITION_Y)
    haltX = Member(0x02C, MemberKind.DWORD)
    haltY = Member(0x030, MemberKind.DWORD)
    topSpeed = Member(0x034, MemberKind.DWORD)
    flingyTopSpeed = Member(0x034, MemberKind.DWORD)
    current_speed1 = Member(0x038, MemberKind.DWORD)
    current_speed2 = Member(0x03C, MemberKind.DWORD)
    current_speedX = Member(0x040, MemberKind.DWORD)
    current_speedY = Member(0x044, MemberKind.DWORD)
    flingyAcceleration = Member(0x048, MemberKind.WORD)
    currentDirection2 = Member(0x04A, MemberKind.BYTE)
    velocityDirection2 = Member(0x04B, MemberKind.BYTE)  # pathing related
    owner = Member(0x04C, MemberKind.TRG_PLAYER)
    playerID = Member(0x04C, MemberKind.TRG_PLAYER)
    order = Member(0x04D, MemberKind.UNIT_ORDER)
    orderID = Member(0x04D, MemberKind.UNIT_ORDER)
    orderState = Member(0x04E, MemberKind.BYTE)
    orderSignal = Member(0x04F, MemberKind.BYTE)
    orderUnitType = Member(0x050, MemberKind.TRG_UNIT)
    _unknown_0x052 = Member(0x052, MemberKind.WORD)  # 2-byte padding
    cooldown = Member(0x054, MemberKind.DWORD)
    orderTimer = Member(0x054, MemberKind.BYTE)
    mainOrderTimer = Member(0x054, MemberKind.BYTE)
    gCooldown = Member(0x055, MemberKind.BYTE)
    groundWeaponCooldown = Member(0x055, MemberKind.BYTE)
    aCooldown = Member(0x056, MemberKind.BYTE)
    airWeaponCooldown = Member(0x056, MemberKind.BYTE)
    spellCooldown = Member(0x057, MemberKind.BYTE)
    orderTargetPos = Member(0x058, MemberKind.POSITION)  # ActionFocus
    orderTargetXY = Member(0x058, MemberKind.POSITION)
    orderTargetX = Member(0x058, MemberKind.POSITION_X)
    orderTargetY = Member(0x05A, MemberKind.POSITION_Y)
    orderTarget = CUnitMember(0x05C)
    orderTargetUnit = CUnitMember(0x05C)
    shield = Member(0x060, MemberKind.DWORD)
    shieldPoints = Member(0x060, MemberKind.DWORD)
    unitID = Member(0x064, MemberKind.TRG_UNIT)
    unitType = Member(0x064, MemberKind.TRG_UNIT)
    _unknown_0x066 = Member(0x066, MemberKind.WORD)  # 2-byte padding
    previousPlayerUnit = CUnitMember(0x068)
    nextPlayerUnit = CUnitMember(0x06C)  # player_link
    subUnit = CUnitMember(0x070)
    orderQHead = UnsupportedMember(0x074, MemberKind.DWORD)
    orderQueueHead = UnsupportedMember(0x074, MemberKind.DWORD)  # COrder
    orderQTail = UnsupportedMember(0x078, MemberKind.DWORD)
    orderQueueTail = UnsupportedMember(0x078, MemberKind.DWORD)
    autoTargetUnit = CUnitMember(0x07C)
    # larva, in-transit, addons
    connectedUnit = CUnitMember(0x080)
    orderQCount = Member(0x084, MemberKind.BYTE)
    orderQueueCount = Member(0x084, MemberKind.BYTE)
    orderQTimer = Member(0x085, MemberKind.BYTE)
    orderQueueTimer = Member(0x085, MemberKind.BYTE)
    _unknown_0x086 = Member(0x086, MemberKind.BYTE)
    attackNotifyTimer = Member(0x087, MemberKind.BYTE)
    # zerg buildings while morphing
    previousUnitType = UnsupportedMember(0x088, MemberKind.TRG_UNIT)
    lastEventTimer = UnsupportedMember(0x08A, MemberKind.BYTE)
    # 17 = was completed (train, morph), 174 = was attacked
    lastEventColor = Member(0x08B, MemberKind.BYTE)
    _unused_0x08C = Member(0x08C, MemberKind.WORD)
    rankIncrease = Member(0x08E, MemberKind.BYTE)
    killCount = Member(0x08F, MemberKind.BYTE)
    lastAttackingPlayer = Member(0x090, MemberKind.TRG_PLAYER)
    secondaryOrderTimer = Member(0x091, MemberKind.BYTE)
    AIActionFlag = Member(0x092, MemberKind.BYTE)
    # 2 = issued an order, 3 = interrupted an order, 4 = hide self before death (self-destruct?)
    userActionFlags = Member(0x093, MemberKind.BYTE)
    currentButtonSet = Member(0x094, MemberKind.WORD)
    isCloaked = Member(0x096, MemberKind.BOOL)
    movementState = Member(0x097, MemberKind.BYTE)
    buildQueue1 = Member(0x098, MemberKind.TRG_UNIT)
    buildQueue2 = Member(0x09A, MemberKind.TRG_UNIT)
    buildQueue3 = Member(0x09C, MemberKind.TRG_UNIT)
    buildQueue4 = Member(0x09E, MemberKind.TRG_UNIT)
    buildQueue5 = Member(0x0A0, MemberKind.TRG_UNIT)
    buildQueue12 = Member(0x098, MemberKind.DWORD)
    buildQueue34 = Member(0x09C, MemberKind.DWORD)
    energy = Member(0x0A2, MemberKind.WORD)
    buildQueueSlot = Member(0x0A4, MemberKind.BYTE)
    uniquenessIdentifier = Member(0x0A5, MemberKind.BYTE)
    targetOrderSpecial = Member(0x0A5, MemberKind.BYTE)
    secondaryOrder = Member(0x0A6, MemberKind.UNIT_ORDER)
    secondaryOrderID = Member(0x0A6, MemberKind.UNIT_ORDER)
    buildingOverlayState = Member(0x0A7, MemberKind.BYTE)
    hpGain = Member(0x0A8, MemberKind.WORD)  # buildRepairHpGain
    shieldGain = Member(0x0AA, MemberKind.WORD)
    remainingBuildTime = Member(0x0AC, MemberKind.WORD)
    previousHP = Member(0x0AE, MemberKind.WORD)
    # alphaID (StoredUnit)
    loadedUnitIndex0 = UnsupportedMember(0x0B0, MemberKind.WORD)
    loadedUnitIndex1 = UnsupportedMember(0x0B2, MemberKind.WORD)
    loadedUnitIndex2 = UnsupportedMember(0x0B4, MemberKind.WORD)
    loadedUnitIndex3 = UnsupportedMember(0x0B6, MemberKind.WORD)
    loadedUnitIndex4 = UnsupportedMember(0x0B8, MemberKind.WORD)
    loadedUnitIndex5 = UnsupportedMember(0x0BA, MemberKind.WORD)
    loadedUnitIndex6 = UnsupportedMember(0x0BC, MemberKind.WORD)
    loadedUnitIndex7 = UnsupportedMember(0x0BE, MemberKind.WORD)
    # union (0xC0 ~ 0xCF) //==================================
    # vulture
    spiderMineCount = Member(0x0C0, MemberKind.BYTE)
    # carrier, reaver
    inHangarChild = CUnitMember(0x0C0)
    outHangarChild = CUnitMember(0x0C4)
    inHangarCount = Member(0x0C8, MemberKind.BYTE)
    outHangarCount = Member(0x0C9, MemberKind.BYTE)
    # interceptor, scarab
    parent = CUnitMember(0x0C0)
    prevFighter = CUnitMember(0x0C4)
    nextFighter = CUnitMember(0x0C8)
    isOutsideHangar = Member(0x0CC, MemberKind.BOOL)
    # beacon
    _beacon_unknown_0xC0 = Member(0x0C0, MemberKind.DWORD)
    _beacon_unknown_0xC4 = Member(0x0C4, MemberKind.DWORD)
    flagSpawnFrame = Member(0x0C8, MemberKind.DWORD)  # beacon
    # building /==============================================
    addon = CUnitMember(0x0C0)
    addonBuildType = Member(0x0C4, MemberKind.TRG_UNIT)
    upgradeResearchTime = Member(0x0C6, MemberKind.WORD)
    techType = Member(0x0C8, MemberKind.TECH)
    upgradeType = Member(0x0C9, MemberKind.UPGRADE)
    larvaTimer = Member(0x0CA, MemberKind.BYTE)
    landingTimer = Member(0x0CB, MemberKind.BYTE)
    creepTimer = Member(0x0CC, MemberKind.BYTE)
    upgradeLevel = Member(0x0CD, MemberKind.BYTE)
    # _padding_CE
    # ==============================================/ building
    # worker
    pPowerup = CUnitMember(0x0C0)
    targetResourcePosition = Member(0x0C4, MemberKind.POSITION)
    targetResourceX = Member(0x0C4, MemberKind.WORD)
    targetResourceY = Member(0x0C6, MemberKind.WORD)
    targetResourceUnit = CUnitMember(0x0C8)
    repairResourceLossTimer = Member(0x0CC, MemberKind.WORD)
    isCarryingSomething = Member(0x0CE, MemberKind.BOOL)
    resourceCarryCount = Member(0x0CF, MemberKind.BYTE)  # worker
    resourceCount = Member(0x0D0, MemberKind.WORD)  # 0x0D0 union
    resourceIscript = Member(0x0D2, MemberKind.BYTE)
    gatherQueueCount = Member(0x0D3, MemberKind.BYTE)
    nextGatherer = CUnitMember(0x0D4)
    resourceGroup = Member(0x0D8, MemberKind.BYTE)
    resourceBelongsToAI = Member(0x0D9, MemberKind.BYTE)
    nydusExit = CUnitMember(0x0D0)
    nukeDot = Member(0x0D0, MemberKind.C_SPRITE)  # ghost
    pPowerTemplate = Member(0x0D0, MemberKind.C_SPRITE)  # Pylon
    pNuke = CUnitMember(0x0D0)
    bReady = Member(0x0D4, MemberKind.BOOL)  # silo
    harvestValueLU = Member(0x0D0, MemberKind.DWORD)  # hatchery
    harvestValueL = Member(0x0D0, MemberKind.WORD)
    harvestValueU = Member(0x0D2, MemberKind.WORD)
    harvestValueRB = Member(0x0D4, MemberKind.DWORD)
    harvestValueR = Member(0x0D4, MemberKind.WORD)
    harvestValueB = Member(0x0D6, MemberKind.WORD)
    originXY = Member(0x0D0, MemberKind.POSITION)
    origin = Member(0x0D0, MemberKind.POSITION)
    originX = Member(0x0D0, MemberKind.WORD)
    originY = Member(0x0D2, MemberKind.WORD)  # powerup
    harvestTarget = CUnitMember(0x0D0)
    prevHarvestUnit = CUnitMember(0x0D4)
    nextHarvestUnit = CUnitMember(0x0D8)  # gatherer
    statusFlags = Member(0x0DC, MemberKind.DWORD)
    # Type of resource chunk carried by this worker.
    # None = 0x00,
    # Vespene = 0x01,
    # Minerals = 0x02,
    # GasOrMineral = 0x03,
    # PowerUp = 0x04
    resourceType = Member(0x0E0, MemberKind.BYTE)
    wireframeRandomizer = Member(0x0E1, MemberKind.BYTE)
    secondaryOrderState = Member(0x0E2, MemberKind.BYTE)
    # Counts down from 15 to 0 when most orders are given, or when the unit moves after reaching a patrol location
    recentOrderTimer = Member(0x0E3, MemberKind.BYTE)
    # which players can detect this unit (cloaked/burrowed)
    visibilityStatus = Member(0x0E4, MemberKind.DWORD)
    secondaryOrderPos = Member(0x0E8, MemberKind.POSITION)
    secondaryOrderX = Member(0x0E8, MemberKind.POSITION_X)
    secondaryOrderY = Member(0x0EA, MemberKind.POSITION_Y)
    currentBuildUnit = CUnitMember(0x0EC)
    prevBurrowedUnit = UnsupportedMember(0x0F0, MemberKind.C_UNIT)
    nextBurrowedUnit = UnsupportedMember(0x0F4, MemberKind.C_UNIT)
    rallyXY = Member(0x0F8, MemberKind.POSITION)
    rallyPosition = Member(0x0F8, MemberKind.POSITION)
    rallyX = Member(0x0F8, MemberKind.WORD)
    rallyY = Member(0x0FA, MemberKind.WORD)
    rallyUnit = CUnitMember(0x0FC)
    prevPsiProvider = CUnitMember(0x0F8)  # not supported?
    nextPsiProvider = CUnitMember(0x0FC)
    path = UnsupportedMember(0x100, MemberKind.DWORD)
    pathingCollisionInterval = Member(0x104, MemberKind.BYTE)
    # 0x01 = uses pathing; 0x02 = ?; 0x04 = ?
    pathingFlags = Member(0x105, MemberKind.BYTE)
    _unused_0x106 = Member(0x106, MemberKind.BYTE)
    # 1 if a medic is currently healing this unit
    isBeingHealed = Member(0x107, MemberKind.BOOL)
    # A rect that specifies the closest contour (collision) points
    contourBoundsLU = UnsupportedMember(0x108, MemberKind.DWORD)
    contourBoundsL = UnsupportedMember(0x108, MemberKind.WORD)
    contourBoundsU = UnsupportedMember(0x10A, MemberKind.WORD)
    contourBoundsRB = UnsupportedMember(0x10C, MemberKind.DWORD)
    contourBoundsR = UnsupportedMember(0x10C, MemberKind.WORD)
    contourBoundsB = UnsupportedMember(0x10E, MemberKind.WORD)
    # Hallucination, Dark Swarm, Disruption Web, Broodling (but not Scanner Sweep according to BWAPI)
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
    irradiatePlayerID = Member(0x120, MemberKind.BYTE)
    # Each bit corresponds to the player who has parasited this unit
    parasiteFlags = Member(0x121, MemberKind.BYTE)
    # counts/cycles up from 0 to 7 (inclusive). See also 0x85
    cycleCounter = Member(0x122, MemberKind.BYTE)
    isBlind = Member(0x123, MemberKind.BYTE)  # is bool in BWAPI
    blindFlags = Member(0x123, MemberKind.BYTE)
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
    # Cycles between 0-12 for each bullet fired by this unit (if it uses a "Attack 3x3 area" weapon)
    offsetIndex3by3 = UnsupportedMember(0x130, MemberKind.WORD)
    _padding_0x132 = UnsupportedMember(0x132, MemberKind.WORD)
    pAI = UnsupportedMember(0x134, MemberKind.DWORD)
    airStrength = UnsupportedMember(0x138, MemberKind.WORD)
    groundStrength = UnsupportedMember(0x13A, MemberKind.WORD)
    finderIndexLeft = UnsupportedMember(0x13C, MemberKind.DWORD)
    finderIndexRight = UnsupportedMember(0x140, MemberKind.DWORD)
    finderIndexTop = UnsupportedMember(0x144, MemberKind.DWORD)
    finderIndexBottom = UnsupportedMember(0x148, MemberKind.DWORD)
    repulseUnknown = Member(0x14C, MemberKind.BYTE)  # updated only when air unit is being pushed
    repulseAngle = Member(0x14D, MemberKind.BYTE)
    driftPos = Member(0x14E, MemberKind.WORD)  # (mapsizex / 1.5 max)
    driftX = Member(0x14E, MemberKind.BYTE)
    driftY = Member(0x14F, MemberKind.BYTE)

    def __init__(self, epd: int_or_var, *, ptr: int_or_var | None = None) -> None:
        """EPD Constructor of CUnit. Use CUnit.from_ptr(ptr) for ptr value"""
        _epd: int | c.EUDVariable
        self._ptr: int | c.EUDVariable | None

        if isinstance(epd, CUnit):
            _epd, self._ptr = epd._epd, epd._ptr
        else:
            u, p = ut.unProxy(epd), ut.unProxy(ptr)
            if isinstance(u, int):
                if p is not None and not isinstance(p, int):
                    raise ut.EPError(_("Invalid input for CUnit: {}").format((epd, ptr)))
                q, r = divmod(u - ut.EPD(0x59CCA8), 84)  # check epd
                if r == 0 and 0 <= q < 1700:
                    _epd, self._ptr = u, 0x59CCA8 + 336 * q
                else:
                    raise ut.EPError(_("Invalid input for CUnit: {}").format((epd, ptr)))
            elif isinstance(u, c.EUDVariable):
                if p is not None and not isinstance(p, c.EUDVariable):
                    raise ut.EPError(_("Invalid input for CUnit: {}").format((epd, ptr)))
                _epd, self._ptr = u, p
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
                raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            epd = EPDCache(u)
        else:
            raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format(epd))

        return cls(epd, ptr=u)

    @classmethod
    def from_read(cls: type[T], epd) -> T:
        _ptr, _epd = f_cunitepdread_epd(epd)
        return cls(_epd, ptr=_ptr)

    @property
    def ptr(self) -> int | c.EUDVariable:
        if self._ptr is not None:
            return self._ptr
        return PtrCache(cast(c.EUDVariable, self._epd))

    def set_color(self, player) -> None:
        player = c.EncodePlayer(player)
        color_epd = c.EUDVariable()
        sprite_epd = self._epd + 0x00C // 4
        if isinstance(sprite_epd, c.EUDVariable):
            check_sprite = c.MemoryEPD(0, c.Exactly, 0)
            c.VProc(sprite_epd, sprite_epd.SetDest(ut.EPD(check_sprite) + 1))
        elif isinstance(sprite_epd, int):
            check_sprite = c.MemoryEPD(sprite_epd, c.Exactly, 0)
        if cs.EUDIfNot()(check_sprite):
            f_spriteepdread_epd(sprite_epd, ret=[ut.EPD(check_sprite) + 2, color_epd])
        cs.EUDEndIf()
        if cs.EUDIfNot()(color_epd <= 2):
            f_bwrite_epd(color_epd + 2, 2, player)
        cs.EUDEndIf()

    def check_status_flag(self, value, mask=None) -> c.Condition:
        if mask is None:
            mask = value
        return c.MemoryXEPD(self._epd + 0x0DC // 4, c.Exactly, value, mask)

    def set_status_flag(self, value, mask=None) -> None:
        if mask is None:
            mask = value
        f_maskwrite_epd(self._epd + 0x0DC // 4, value, mask)

    def clear_status_flag(self, mask) -> None:
        f_maskwrite_epd(self._epd + 0x0DC // 4, 0, mask)

    def reset_buildq(self, Q1=0xE4) -> None:
        self.buildQ12 = 0xE40000 + Q1
        self.buildQ34 = 0xE400E4
        self.buildQ5 = 0xE4

    def die(self) -> None:
        self.order = 0

    def remove_collision(self) -> None:
        self.set_status_flag(0x00A00000)

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
        ut.ep_assert(not IsUnlimiterOn(), "Can't detect unit dying with [unlimiter]")
        return (self.order == 0, self.sprite >= 1)

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
        f_setloc_epd(location, self._epd + 0x28 // 4)


EPDCUnitMap = CUnit
