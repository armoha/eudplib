#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2023 Armoha

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from collections.abc import Mapping
from typing import cast, ClassVar, TypeAlias, TypeVar

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from .locf import f_setloc_epd
from .memiof import (
    f_bwrite_epd,
    f_cunitepdread_epd,
    f_maskwrite_epd,
    f_spriteepdread_epd,
)
from .utilf.unlimiterflag import IsUnlimiterOn
from .epdoffsetmap import CUnitMember, MemberKind, Member, EPDOffsetMap, EPDCache, PtrCache


T = TypeVar("T", bound="CUnit")
int_or_var: TypeAlias = int | c.EUDVariable | ut.ExprProxy


class CUnit(EPDOffsetMap):
    __slots__ = "_ptr"

    prev = CUnitMember("prev", 0x000, MemberKind.C_UNIT)
    next = CUnitMember("next", 0x004, MemberKind.C_UNIT)  # link
    hp = Member("hp", 0x008, MemberKind.DWORD)
    # displayed value is ceil(healthPoints/256)
    hitPoints = Member("hitPoints", 0x008, MemberKind.DWORD)
    sprite = Member("sprite", 0x00C, MemberKind.C_SPRITE)
    moveTargetXY = Member("moveTargetXY", 0x010, MemberKind.POSITION)
    moveTargetPosition = Member("moveTargetPosition", 0x010, MemberKind.POSITION)
    moveTargetX = Member("moveTargetX", 0x010, MemberKind.POSITION_X)
    moveTargetY = Member("moveTargetY", 0x012, MemberKind.POSITION_Y)
    moveTarget = CUnitMember("moveTarget", 0x014, MemberKind.C_UNIT)
    moveTargetUnit = CUnitMember("moveTargetUnit", 0x014, MemberKind.C_UNIT)
    # The next way point in the path the unit is following to get to its destination.
    # Equal to moveToPos for air units since they don't need to navigate around buildings.
    nextMovementWaypoint = Member("nextMovementWaypoint", 0x018, MemberKind.POSITION)
    # The desired position
    nextTargetWaypoint = Member("nextTargetWaypoint", 0x01C, MemberKind.POSITION)
    movementFlags = Member("movementFlags", 0x020, MemberKind.BYTE)
    direction = Member("direction", 0x021, MemberKind.BYTE)
    # current direction the unit is facing
    currentDirection1 = Member("currentDirection1", 0x021, MemberKind.BYTE)
    flingyTurnRadius = Member("flingyTurnRadius", 0x022, MemberKind.BYTE)
    flingyTurnSpeed = Member("flingyTurnSpeed", 0x022, MemberKind.BYTE)
    velocityDirection1 = Member("velocityDirection1", 0x023, MemberKind.BYTE)
    flingyID = Member("flingyID", 0x024, MemberKind.FLINGY)
    _unknown_0x026 = Member("_unknown_0x026", 0x026, MemberKind.BYTE)
    flingyMovementType = Member("flingyMovementType", 0x027, MemberKind.BYTE)
    pos = Member("pos", 0x028, MemberKind.POSITION)
    position = Member("position", 0x028, MemberKind.POSITION)
    posX = Member("posX", 0x028, MemberKind.POSITION_X)
    positionX = Member("positionX", 0x028, MemberKind.POSITION_X)
    posY = Member("posY", 0x02A, MemberKind.POSITION_Y)
    positionY = Member("positionY", 0x02A, MemberKind.POSITION_Y)
    haltX = Member("haltX", 0x02C, MemberKind.DWORD)
    haltY = Member("haltY", 0x030, MemberKind.DWORD)
    topSpeed = Member("topSpeed", 0x034, MemberKind.DWORD)
    flingyTopSpeed = Member("flingyTopSpeed", 0x034, MemberKind.DWORD)
    current_speed1 = Member("current_speed1", 0x038, MemberKind.DWORD)
    current_speed2 = Member("current_speed2", 0x03C, MemberKind.DWORD)
    current_speedX = Member("current_speedX", 0x040, MemberKind.DWORD)
    current_speedY = Member("current_speedY", 0x044, MemberKind.DWORD)
    flingyAcceleration = Member("flingyAcceleration", 0x048, MemberKind.WORD)
    currentDirection2 = Member("currentDirection2", 0x04A, MemberKind.BYTE)
    velocityDirection2 = Member("velocityDirection2", 0x04B, MemberKind.BYTE)  # pathing related
    owner = Member("owner", 0x04C, MemberKind.TRG_PLAYER)
    playerID = Member("playerID", 0x04C, MemberKind.TRG_PLAYER)
    order = Member("order", 0x04D, MemberKind.BYTE)
    orderID = Member("orderID", 0x04D, MemberKind.BYTE)
    orderState = Member("orderState", 0x04E, MemberKind.BYTE)
    orderSignal = Member("orderSignal", 0x04F, MemberKind.BYTE)
    orderUnitType = Member("orderUnitType", 0x050, MemberKind.TRG_UNIT)
    _unknown_0x052 = Member("_unknown_0x052", 0x052, MemberKind.WORD)  # 2-byte padding
    cooldown = Member("cooldown", 0x054, MemberKind.DWORD)
    orderTimer = Member("orderTimer", 0x054, MemberKind.BYTE)
    mainOrderTimer = Member("mainOrderTimer", 0x054, MemberKind.BYTE)
    gCooldown = Member("gCooldown", 0x055, MemberKind.BYTE)
    groundWeaponCooldown = Member("groundWeaponCooldown", 0x055, MemberKind.BYTE)
    aCooldown = Member("aCooldown", 0x056, MemberKind.BYTE)
    airWeaponCooldown = Member("airWeaponCooldown", 0x056, MemberKind.BYTE)
    spellCooldown = Member("spellCooldown", 0x057, MemberKind.BYTE)
    orderTargetXY = Member("orderTargetXY", 0x058, MemberKind.POSITION)
    orderTargetPosition = Member("orderTargetPosition", 0x058, MemberKind.POSITION)  # ActionFocus
    orderTargetX = Member("orderTargetX", 0x058, MemberKind.POSITION_X)
    orderTargetY = Member("orderTargetY", 0x05A, MemberKind.POSITION_Y)
    orderTarget = CUnitMember("orderTarget", 0x05C, MemberKind.C_UNIT)
    orderTargetUnit = CUnitMember("orderTargetUnit", 0x05C, MemberKind.C_UNIT)
    shield = Member("shield", 0x060, MemberKind.DWORD)
    shieldPoints = Member("shieldPoints", 0x060, MemberKind.DWORD)
    unitId = Member("unitId", 0x064, MemberKind.TRG_UNIT)
    unitType = Member("unitType", 0x064, MemberKind.TRG_UNIT)
    _unknown_0x066 = Member("_unknown_0x066", 0x066, MemberKind.WORD)  # 2-byte padding
    previousPlayerUnit = CUnitMember("previousPlayerUnit", 0x068, MemberKind.C_UNIT)
    nextPlayerUnit = CUnitMember("nextPlayerUnit", 0x06C, MemberKind.C_UNIT)  # player_link
    subUnit = CUnitMember("subUnit", 0x070, MemberKind.C_UNIT)
    orderQHead = Member("orderQHead", 0x074, MemberKind.DWORD)
    orderQueueHead = Member("orderQueueHead", 0x074, MemberKind.DWORD)  # COrder
    orderQTail = Member("orderQTail", 0x078, MemberKind.DWORD)
    orderQueueTail = Member("orderQueueTail", 0x078, MemberKind.DWORD)
    autoTargetUnit = CUnitMember("autoTargetUnit", 0x07C, MemberKind.C_UNIT)
    # larva, in-transit, addons
    connectedUnit = CUnitMember("connectedUnit", 0x080, MemberKind.C_UNIT)
    orderQCount = Member("orderQCount", 0x084, MemberKind.BYTE)
    orderQueueCount = Member("orderQueueCount", 0x084, MemberKind.BYTE)
    orderQTimer = Member("orderQTimer", 0x085, MemberKind.BYTE)
    orderQueueTimer = Member("orderQueueTimer", 0x085, MemberKind.BYTE)
    _unknown_0x086 = Member("_unknown_0x086", 0x086, MemberKind.BYTE)
    attackNotifyTimer = Member("attackNotifyTimer", 0x087, MemberKind.BYTE)
    # zerg buildings while morphing
    previousUnitType = Member("previousUnitType", 0x088, MemberKind.TRG_UNIT)
    lastEventTimer = Member("lastEventTimer", 0x08A, MemberKind.BYTE)
    # 17 = was completed (train, morph), 174 = was attacked
    lastEventColor = Member("lastEventColor", 0x08B, MemberKind.BYTE)
    _unused_0x08C = Member("_unused_0x08C", 0x08C, MemberKind.WORD)
    rankIncrease = Member("rankIncrease", 0x08E, MemberKind.BYTE)
    killCount = Member("killCount", 0x08F, MemberKind.BYTE)
    lastAttackingPlayer = Member("lastAttackingPlayer", 0x090, MemberKind.TRG_PLAYER)
    secondaryOrderTimer = Member("secondaryOrderTimer", 0x091, MemberKind.BYTE)
    AIActionFlag = Member("AIActionFlag", 0x092, MemberKind.BYTE)
    # 2 = issued an order, 3 = interrupted an order, 4 = hide self before death (self-destruct?)
    userActionFlags = Member("userActionFlags", 0x093, MemberKind.BYTE)
    currentButtonSet = Member("currentButtonSet", 0x094, MemberKind.WORD)
    isCloaked = Member("isCloaked", 0x096, MemberKind.BOOL)
    movementState = Member("movementState", 0x097, MemberKind.BYTE)
    buildQ12 = Member("buildQ12", 0x098, MemberKind.DWORD)
    buildQ1 = Member("buildQ1", 0x098, MemberKind.TRG_UNIT)
    buildQueue1 = Member("buildQueue1", 0x098, MemberKind.TRG_UNIT)
    buildQ2 = Member("buildQ2", 0x09A, MemberKind.TRG_UNIT)
    buildQueue2 = Member("buildQueue2", 0x09A, MemberKind.TRG_UNIT)
    buildQ34 = Member("buildQ34", 0x09C, MemberKind.DWORD)
    buildQ3 = Member("buildQ3", 0x09C, MemberKind.TRG_UNIT)
    buildQueue3 = Member("buildQueue3", 0x09C, MemberKind.TRG_UNIT)
    buildQ4 = Member("buildQ4", 0x09E, MemberKind.TRG_UNIT)
    buildQueue4 = Member("buildQueue4", 0x09E, MemberKind.TRG_UNIT)
    buildQ5 = Member("buildQ5", 0x0A0, MemberKind.TRG_UNIT)
    buildQueue5 = Member("buildQueue5", 0x0A0, MemberKind.TRG_UNIT)
    energy = Member("energy", 0x0A2, MemberKind.WORD)
    buildQueueSlot = Member("buildQueueSlot", 0x0A4, MemberKind.BYTE)
    uniquenessIdentifier = Member("uniquenessIdentifier", 0x0A5, MemberKind.BYTE)
    targetOrderSpecial = Member("targetOrderSpecial", 0x0A5, MemberKind.BYTE)
    secondaryOrder = Member("secondaryOrder", 0x0A6, MemberKind.BYTE)
    secondaryOrderID = Member("secondaryOrderID", 0x0A6, MemberKind.BYTE)
    buildingOverlayState = Member("buildingOverlayState", 0x0A7, MemberKind.BYTE)
    hpGain = Member("hpGain", 0x0A8, MemberKind.WORD)  # buildRepairHpGain
    shieldGain = Member("shieldGain", 0x0AA, MemberKind.WORD)
    remainingBuildTime = Member("remainingBuildTime", 0x0AC, MemberKind.WORD)
    previousHP = Member("previousHP", 0x0AE, MemberKind.WORD)
    # alphaID (StoredUnit)
    loadedUnitIndex0 = Member("loadedUnitIndex0", 0x0B0, MemberKind.WORD)
    loadedUnitIndex1 = Member("loadedUnitIndex1", 0x0B2, MemberKind.WORD)
    loadedUnitIndex2 = Member("loadedUnitIndex2", 0x0B4, MemberKind.WORD)
    loadedUnitIndex3 = Member("loadedUnitIndex3", 0x0B6, MemberKind.WORD)
    loadedUnitIndex4 = Member("loadedUnitIndex4", 0x0B8, MemberKind.WORD)
    loadedUnitIndex5 = Member("loadedUnitIndex5", 0x0BA, MemberKind.WORD)
    loadedUnitIndex6 = Member("loadedUnitIndex6", 0x0BC, MemberKind.WORD)
    loadedUnitIndex7 = Member("loadedUnitIndex7", 0x0BE, MemberKind.WORD)
    mineCount = Member("mineCount", 0x0C0, MemberKind.BYTE)  # 0x0C0 union, vulture
    spiderMineCount = Member("spiderMineCount", 0x0C0, MemberKind.BYTE)
    pInHanger = CUnitMember("pInHanger", 0x0C0, MemberKind.C_UNIT)
    pOutHanger = CUnitMember("pOutHanger", 0x0C4, MemberKind.C_UNIT)
    inHangerCount = Member("inHangerCount", 0x0C8, MemberKind.BYTE)
    outHangerCount = Member("outHangerCount", 0x0C9, MemberKind.BYTE)  # carrier
    parent = CUnitMember("parent", 0x0C0, MemberKind.C_UNIT)
    prevFighter = CUnitMember("prevFighter", 0x0C4, MemberKind.C_UNIT)
    nextFighter = CUnitMember("nextFighter", 0x0C8, MemberKind.C_UNIT)
    inHanger = Member("inHanger", 0x0CC, MemberKind.BOOL)
    isOutsideHangar = Member("isOutsideHangar", 0x0CC, MemberKind.BOOL)  # fighter
    _unknown_00 = Member("_unknown_00", 0x0C0, MemberKind.DWORD)
    _unknown_04 = Member("_unknown_04", 0x0C4, MemberKind.DWORD)
    flagSpawnFrame = Member("flagSpawnFrame", 0x0C8, MemberKind.DWORD)  # beacon
    addon = CUnitMember("addon", 0x0C0, MemberKind.C_UNIT)
    addonBuildType = Member("addonBuildType", 0x0C4, MemberKind.TRG_UNIT)
    upgradeResearchTime = Member("upgradeResearchTime", 0x0C6, MemberKind.WORD)
    techType = Member("techType", 0x0C8, MemberKind.TECH)
    upgradeType = Member("upgradeType", 0x0C9, MemberKind.UPGRADE)
    larvaTimer = Member("larvaTimer", 0x0CA, MemberKind.BYTE)
    landingTimer = Member("landingTimer", 0x0CB, MemberKind.BYTE)
    creepTimer = Member("creepTimer", 0x0CC, MemberKind.BYTE)
    upgradeLevel = Member("upgradeLevel", 0x0CD, MemberKind.BYTE)
    __E = Member("__E", 0x0CE, MemberKind.WORD)  # building
    pPowerup = CUnitMember("pPowerup", 0x0C0, MemberKind.C_UNIT)
    targetResourcePosition = Member("targetResourcePosition", 0x0C4, MemberKind.POSITION)
    targetResourceX = Member("targetResourceX", 0x0C4, MemberKind.WORD)
    targetResourceY = Member("targetResourceY", 0x0C6, MemberKind.WORD)
    targetResourceUnit = CUnitMember("targetResourceUnit", 0x0C8, MemberKind.C_UNIT)
    repairResourceLossTimer = Member("repairResourceLossTimer", 0x0CC, MemberKind.WORD)
    isCarryingSomething = Member("isCarryingSomething", 0x0CE, MemberKind.BOOL)
    resourceCarryCount = Member("resourceCarryCount", 0x0CF, MemberKind.BYTE)  # worker
    resourceCount = Member("resourceCount", 0x0D0, MemberKind.WORD)  # 0x0D0 union
    resourceIscript = Member("resourceIscript", 0x0D2, MemberKind.BYTE)
    gatherQueueCount = Member("gatherQueueCount", 0x0D3, MemberKind.BYTE)
    nextGatherer = CUnitMember("nextGatherer", 0x0D4, MemberKind.C_UNIT)
    resourceGroup = Member("resourceGroup", 0x0D8, MemberKind.BYTE)
    resourceBelongsToAI = Member("resourceBelongsToAI", 0x0D9, MemberKind.BYTE)
    nydusExit = CUnitMember("nydusExit", 0x0D0, MemberKind.C_UNIT)
    nukeDot = Member("nukeDot", 0x0D0, MemberKind.C_SPRITE)  # ghost
    pPowerTemplate = Member("pPowerTemplate", 0x0D0, MemberKind.C_SPRITE)  # Pylon
    pNuke = CUnitMember("pNuke", 0x0D0, MemberKind.C_UNIT)
    bReady = Member("bReady", 0x0D4, MemberKind.BOOL)  # silo
    harvestValueLU = Member("harvestValueLU", 0x0D0, MemberKind.DWORD)  # hatchery
    harvestValueL = Member("harvestValueL", 0x0D0, MemberKind.WORD)
    harvestValueU = Member("harvestValueU", 0x0D2, MemberKind.WORD)
    harvestValueRB = Member("harvestValueRB", 0x0D4, MemberKind.DWORD)
    harvestValueR = Member("harvestValueR", 0x0D4, MemberKind.WORD)
    harvestValueB = Member("harvestValueB", 0x0D6, MemberKind.WORD)
    originXY = Member("originXY", 0x0D0, MemberKind.POSITION)
    origin = Member("origin", 0x0D0, MemberKind.POSITION)
    originX = Member("originX", 0x0D0, MemberKind.WORD)
    originY = Member("originY", 0x0D2, MemberKind.WORD)  # powerup
    harvestTarget = CUnitMember("harvestTarget", 0x0D0, MemberKind.C_UNIT)
    prevHarvestUnit = CUnitMember("prevHarvestUnit", 0x0D4, MemberKind.C_UNIT)
    nextHarvestUnit = CUnitMember("nextHarvestUnit", 0x0D8, MemberKind.C_UNIT)  # gatherer
    statusFlags = Member("statusFlags", 0x0DC, MemberKind.DWORD)
    resourceType = Member("resourceType", 0x0E0, MemberKind.BYTE)
    wireframeRandomizer = Member("wireframeRandomizer", 0x0E1, MemberKind.BYTE)
    secondaryOrderState = Member("secondaryOrderState", 0x0E2, MemberKind.BYTE)
    recentOrderTimer = Member("recentOrderTimer", 0x0E3, MemberKind.BYTE)
    # which players can detect this unit (cloaked/burrowed)
    visibilityStatus = Member("visibilityStatus", 0x0E4, MemberKind.DWORD)
    secondaryOrderPosition = Member("secondaryOrderPosition", 0x0E8, MemberKind.POSITION)
    secondaryOrderX = Member("secondaryOrderX", 0x0E8, MemberKind.WORD)
    secondaryOrderY = Member("secondaryOrderY", 0x0EA, MemberKind.WORD)
    currentBuildUnit = CUnitMember("currentBuildUnit", 0x0EC, MemberKind.C_UNIT)
    previousBurrowedUnit = CUnitMember("previousBurrowedUnit", 0x0F0, MemberKind.C_UNIT)
    nextBurrowedUnit = CUnitMember("nextBurrowedUnit", 0x0F4, MemberKind.C_UNIT)
    rallyXY = Member("rallyXY", 0x0F8, MemberKind.POSITION)
    rallyPosition = Member("rallyPosition", 0x0F8, MemberKind.POSITION)
    rallyX = Member("rallyX", 0x0F8, MemberKind.WORD)
    rallyY = Member("rallyY", 0x0FA, MemberKind.WORD)
    rallyUnit = CUnitMember("rallyUnit", 0x0FC, MemberKind.C_UNIT)
    prevPsiProvider = CUnitMember("prevPsiProvider", 0x0F8, MemberKind.C_UNIT)
    nextPsiProvider = CUnitMember("nextPsiProvider", 0x0FC, MemberKind.C_UNIT)
    path = Member("path", 0x100, MemberKind.DWORD)
    pathingCollisionInterval = Member("pathingCollisionInterval", 0x104, MemberKind.BYTE)
    pathingFlags = Member("pathingFlags", 0x105, MemberKind.BYTE)
    _unused_0x106 = Member("_unused_0x106", 0x106, MemberKind.BYTE)
    isBeingHealed = Member("isBeingHealed", 0x107, MemberKind.BOOL)
    contourBoundsLU = Member("contourBoundsLU", 0x108, MemberKind.DWORD)
    contourBoundsL = Member("contourBoundsL", 0x108, MemberKind.WORD)
    contourBoundsU = Member("contourBoundsU", 0x10A, MemberKind.WORD)
    contourBoundsRB = Member("contourBoundsRB", 0x10C, MemberKind.DWORD)
    contourBoundsR = Member("contourBoundsR", 0x10C, MemberKind.WORD)
    contourBoundsB = Member("contourBoundsB", 0x10E, MemberKind.WORD)
    removeTimer = Member("removeTimer", 0x110, MemberKind.WORD)
    matrixDamage = Member("matrixDamage", 0x112, MemberKind.WORD)
    defenseMatrixDamage = Member("defenseMatrixDamage", 0x112, MemberKind.WORD)
    defensiveMatrixHp = Member("defensiveMatrixHp", 0x112, MemberKind.WORD)
    matrixTimer = Member("matrixTimer", 0x114, MemberKind.BYTE)
    defenseMatrixTimer = Member("defenseMatrixTimer", 0x114, MemberKind.BYTE)
    stimTimer = Member("stimTimer", 0x115, MemberKind.BYTE)
    ensnareTimer = Member("ensnareTimer", 0x116, MemberKind.BYTE)
    lockdownTimer = Member("lockdownTimer", 0x117, MemberKind.BYTE)
    irradiateTimer = Member("irradiateTimer", 0x118, MemberKind.BYTE)
    stasisTimer = Member("stasisTimer", 0x119, MemberKind.BYTE)
    plagueTimer = Member("plagueTimer", 0x11A, MemberKind.BYTE)
    stormTimer = Member("stormTimer", 0x11B, MemberKind.BYTE)
    isUnderStorm = Member("isUnderStorm", 0x11B, MemberKind.BYTE)
    irradiatedBy = CUnitMember("irradiatedBy", 0x11C, MemberKind.C_UNIT)
    irradiatePlayerID = Member("irradiatePlayerID", 0x120, MemberKind.BYTE)
    parasiteFlags = Member("parasiteFlags", 0x121, MemberKind.BYTE)
    cycleCounter = Member("cycleCounter", 0x122, MemberKind.BYTE)
    isBlind = Member("isBlind", 0x123, MemberKind.BYTE)
    blindFlags = Member("blindFlags", 0x123, MemberKind.BYTE)
    maelstromTimer = Member("maelstromTimer", 0x124, MemberKind.BYTE)
    _unused_0x125 = Member("_unused_0x125", 0x125, MemberKind.BYTE)
    unusedTimer = Member("unusedTimer", 0x125, MemberKind.BYTE)
    acidSporeCount = Member("acidSporeCount", 0x126, MemberKind.BYTE)
    acidSporeTime0 = Member("acidSporeTime0", 0x127, MemberKind.BYTE)
    acidSporeTime1 = Member("acidSporeTime1", 0x128, MemberKind.BYTE)
    acidSporeTime2 = Member("acidSporeTime2", 0x129, MemberKind.BYTE)
    acidSporeTime3 = Member("acidSporeTime3", 0x12A, MemberKind.BYTE)
    acidSporeTime4 = Member("acidSporeTime4", 0x12B, MemberKind.BYTE)
    acidSporeTime5 = Member("acidSporeTime5", 0x12C, MemberKind.BYTE)
    acidSporeTime6 = Member("acidSporeTime6", 0x12D, MemberKind.BYTE)
    acidSporeTime7 = Member("acidSporeTime7", 0x12E, MemberKind.BYTE)
    acidSporeTime8 = Member("acidSporeTime8", 0x12F, MemberKind.BYTE)
    bulletBehaviour3by3AttackSequence = Member(
        "bulletBehaviour3by3AttackSequence", 0x130, MemberKind.WORD
    )
    offsetIndex3by3 = Member("offsetIndex3by3", 0x130, MemberKind.WORD)
    _padding_0x132 = Member("_padding_0x132", 0x132, MemberKind.WORD)
    pAI = Member("pAI", 0x134, MemberKind.DWORD)
    airStrength = Member("airStrength", 0x138, MemberKind.WORD)
    groundStrength = Member("groundStrength", 0x13A, MemberKind.WORD)
    finderIndexLeft = Member("finderIndexLeft", 0x13C, MemberKind.DWORD)
    finderIndexRight = Member("finderIndexRight", 0x140, MemberKind.DWORD)
    finderIndexTop = Member("finderIndexTop", 0x144, MemberKind.DWORD)
    finderIndexBottom = Member("finderIndexBottom", 0x148, MemberKind.DWORD)
    repulseUnknown = Member("repulseUnknown", 0x14C, MemberKind.BYTE)
    repulseAngle = Member("repulseAngle", 0x14D, MemberKind.BYTE)
    driftPos = Member("driftPos", 0x14E, MemberKind.WORD)
    bRepMtxXY = Member("bRepMtxXY", 0x14E, MemberKind.WORD)  # mapsizex / 1.5 max
    bRepMtxX = Member("bRepMtxX", 0x14E, MemberKind.BYTE)
    bRepMtxY = Member("bRepMtxY", 0x14F, MemberKind.BYTE)
    driftPosX = Member("driftPosX", 0x14E, MemberKind.BYTE)
    driftPosY = Member("driftPosY", 0x14F, MemberKind.BYTE)

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
                    raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format((epd, ptr)))
                q, r = divmod(u - ut.EPD(0x59CCA8), 84)  # check epd
                if r == 0 and 0 <= q < 1700:
                    _epd, self._ptr = u, 0x59CCA8 + 336 * q
                else:
                    raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format((epd, ptr)))
            elif isinstance(u, c.EUDVariable):
                if p is not None and not isinstance(p, c.EUDVariable):
                    raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format((epd, ptr)))
                _epd, self._ptr = u, p
            else:
                raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format((epd, ptr)))

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

    def is_in_building(self) -> c.Condition:
        return self.check_status_flag(0x00000020)

    def is_in_transport(self) -> c.Condition:
        return self.check_status_flag(0x00000040)

    def is_burrowed(self) -> c.Condition:
        return self.check_status_flag(0x00000010)

    def setloc(self, location) -> None:
        f_setloc_epd(location, self._epd + 0x28 // 4)


EPDCUnitMap = CUnit
