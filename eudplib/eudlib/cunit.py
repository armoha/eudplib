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
from typing import ClassVar, TypeAlias, TypeVar

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
from .epdoffsetmap import MemberKind, Member, EPDOffsetMap, EPDCache, PtrCache


T = TypeVar("T", bound="CUnit")
int_or_var: TypeAlias = int | c.EUDVariable | ut.ExprProxy


class CUnit(EPDOffsetMap):
    members: ClassVar[Mapping[str, Member]] = {
        "prev": Member("prev", 0x000, MemberKind.C_UNIT),
        "next": Member("next", 0x004, MemberKind.C_UNIT),  # link
        "hp": Member("hp", 0x008, MemberKind.DWORD),
        # displayed value is ceil(healthPoints/256)
        "hitPoints": Member("hitPoints", 0x008, MemberKind.DWORD),
        "sprite": Member("sprite", 0x00C, MemberKind.C_SPRITE),
        "moveTargetXY": Member("moveTargetXY", 0x010, MemberKind.POSITION),
        "moveTargetPosition": Member("moveTargetPosition", 0x010, MemberKind.POSITION),
        "moveTargetX": Member("moveTargetX", 0x010, MemberKind.POSITION_X),
        "moveTargetY": Member("moveTargetY", 0x012, MemberKind.POSITION_Y),
        "moveTarget": Member("moveTarget", 0x014, MemberKind.C_UNIT),
        "moveTargetUnit": Member("moveTargetUnit", 0x014, MemberKind.C_UNIT),
        # The next way point in the path the unit is following to get to its destination.
        # Equal to moveToPos for air units since they don't need to navigate around buildings.
        "nextMovementWaypoint": Member("nextMovementWaypoint", 0x018, MemberKind.POSITION),
        # The desired position
        "nextTargetWaypoint": Member("nextTargetWaypoint", 0x01C, MemberKind.POSITION),
        "movementFlags": Member("movementFlags", 0x020, MemberKind.BYTE),
        "direction": Member("direction", 0x021, MemberKind.BYTE),
        # current direction the unit is facing
        "currentDirection1": Member("currentDirection1", 0x021, MemberKind.BYTE),
        "flingyTurnRadius": Member("flingyTurnRadius", 0x022, MemberKind.BYTE),
        "flingyTurnSpeed": Member("flingyTurnSpeed", 0x022, MemberKind.BYTE),
        "velocityDirection1": Member("velocityDirection1", 0x023, MemberKind.BYTE),
        "flingyID": Member("flingyID", 0x024, MemberKind.FLINGY),
        "_unknown_0x026": Member("_unknown_0x026", 0x026, MemberKind.BYTE),
        "flingyMovementType": Member("flingyMovementType", 0x027, MemberKind.BYTE),
        "pos": Member("pos", 0x028, MemberKind.POSITION),
        "position": Member("position", 0x028, MemberKind.POSITION),
        "posX": Member("posX", 0x028, MemberKind.POSITION_X),
        "positionX": Member("positionX", 0x028, MemberKind.POSITION_X),
        "posY": Member("posY", 0x02A, MemberKind.POSITION_Y),
        "positionY": Member("positionY", 0x02A, MemberKind.POSITION_Y),
        "haltX": Member("haltX", 0x02C, MemberKind.DWORD),
        "haltY": Member("haltY", 0x030, MemberKind.DWORD),
        "topSpeed": Member("topSpeed", 0x034, MemberKind.DWORD),
        "flingyTopSpeed": Member("flingyTopSpeed", 0x034, MemberKind.DWORD),
        "current_speed1": Member("current_speed1", 0x038, MemberKind.DWORD),
        "current_speed2": Member("current_speed2", 0x03C, MemberKind.DWORD),
        "current_speedX": Member("current_speedX", 0x040, MemberKind.DWORD),
        "current_speedY": Member("current_speedY", 0x044, MemberKind.DWORD),
        "flingyAcceleration": Member("flingyAcceleration", 0x048, MemberKind.WORD),
        "currentDirection2": Member("currentDirection2", 0x04A, MemberKind.BYTE),
        # pathing related
        "velocityDirection2": Member("velocityDirection2", 0x04B, MemberKind.BYTE),
        "owner": Member("owner", 0x04C, MemberKind.TRG_PLAYER),
        "playerID": Member("playerID", 0x04C, MemberKind.TRG_PLAYER),
        "order": Member("order", 0x04D, MemberKind.BYTE),
        "orderID": Member("orderID", 0x04D, MemberKind.BYTE),
        "orderState": Member("orderState", 0x04E, MemberKind.BYTE),
        "orderSignal": Member("orderSignal", 0x04F, MemberKind.BYTE),
        "orderUnitType": Member("orderUnitType", 0x050, MemberKind.TRG_UNIT),
        "_unknown_0x052": Member("_unknown_0x052", 0x052, MemberKind.WORD),  # 2-byte padding
        "cooldown": Member("cooldown", 0x054, MemberKind.DWORD),
        "orderTimer": Member("orderTimer", 0x054, MemberKind.BYTE),
        "mainOrderTimer": Member("mainOrderTimer", 0x054, MemberKind.BYTE),
        "gCooldown": Member("gCooldown", 0x055, MemberKind.BYTE),
        "groundWeaponCooldown": Member("groundWeaponCooldown", 0x055, MemberKind.BYTE),
        "aCooldown": Member("aCooldown", 0x056, MemberKind.BYTE),
        "airWeaponCooldown": Member("airWeaponCooldown", 0x056, MemberKind.BYTE),
        "spellCooldown": Member("spellCooldown", 0x057, MemberKind.BYTE),
        "orderTargetXY": Member("orderTargetXY", 0x058, MemberKind.POSITION),
        "orderTargetPosition": Member(
            "orderTargetPosition", 0x058, MemberKind.POSITION
        ),  # ActionFocus
        "orderTargetX": Member("orderTargetX", 0x058, MemberKind.POSITION_X),
        "orderTargetY": Member("orderTargetY", 0x05A, MemberKind.POSITION_Y),
        "orderTarget": Member("orderTarget", 0x05C, MemberKind.C_UNIT),
        "orderTargetUnit": Member("orderTargetUnit", 0x05C, MemberKind.C_UNIT),
        "shield": Member("shield", 0x060, MemberKind.DWORD),
        "shieldPoints": Member("shieldPoints", 0x060, MemberKind.DWORD),
        "unitId": Member("unitId", 0x064, MemberKind.TRG_UNIT),
        "unitType": Member("unitType", 0x064, MemberKind.TRG_UNIT),
        "_unknown_0x066": Member("_unknown_0x066", 0x066, MemberKind.WORD),  # 2-byte padding
        "previousPlayerUnit": Member("previousPlayerUnit", 0x068, MemberKind.C_UNIT),
        "nextPlayerUnit": Member("nextPlayerUnit", 0x06C, MemberKind.C_UNIT),  # player_link
        "subUnit": Member("subUnit", 0x070, MemberKind.C_UNIT),
        "orderQHead": Member("orderQHead", 0x074, MemberKind.DWORD),
        "orderQueueHead": Member("orderQueueHead", 0x074, MemberKind.DWORD),  # COrder
        "orderQTail": Member("orderQTail", 0x078, MemberKind.DWORD),
        "orderQueueTail": Member("orderQueueTail", 0x078, MemberKind.DWORD),
        "autoTargetUnit": Member("autoTargetUnit", 0x07C, MemberKind.C_UNIT),
        # larva, in-transit, addons
        "connectedUnit": Member("connectedUnit", 0x080, MemberKind.C_UNIT),
        "orderQCount": Member("orderQCount", 0x084, MemberKind.BYTE),
        "orderQueueCount": Member("orderQueueCount", 0x084, MemberKind.BYTE),
        "orderQTimer": Member("orderQTimer", 0x085, MemberKind.BYTE),
        "orderQueueTimer": Member("orderQueueTimer", 0x085, MemberKind.BYTE),
        "_unknown_0x086": Member("_unknown_0x086", 0x086, MemberKind.BYTE),
        "attackNotifyTimer": Member("attackNotifyTimer", 0x087, MemberKind.BYTE),
        # zerg buildings while morphing
        "previousUnitType": Member("previousUnitType", 0x088, MemberKind.TRG_UNIT),
        "lastEventTimer": Member("lastEventTimer", 0x08A, MemberKind.BYTE),
        # 17 = was completed (train, morph), 174 = was attacked
        "lastEventColor": Member("lastEventColor", 0x08B, MemberKind.BYTE),
        "_unused_0x08C": Member("_unused_0x08C", 0x08C, MemberKind.WORD),
        "rankIncrease": Member("rankIncrease", 0x08E, MemberKind.BYTE),
        "killCount": Member("killCount", 0x08F, MemberKind.BYTE),
        "lastAttackingPlayer": Member("lastAttackingPlayer", 0x090, MemberKind.TRG_PLAYER),
        "secondaryOrderTimer": Member("secondaryOrderTimer", 0x091, MemberKind.BYTE),
        "AIActionFlag": Member("AIActionFlag", 0x092, MemberKind.BYTE),
        # 2 = issued an order, 3 = interrupted an order, 4 = hide self before death (self-destruct?)
        "userActionFlags": Member("userActionFlags", 0x093, MemberKind.BYTE),
        "currentButtonSet": Member("currentButtonSet", 0x094, MemberKind.WORD),
        "isCloaked": Member("isCloaked", 0x096, MemberKind.BOOL),
        "movementState": Member("movementState", 0x097, MemberKind.BYTE),
        "buildQ12": Member("buildQ12", 0x098, MemberKind.DWORD),
        "buildQ1": Member("buildQ1", 0x098, MemberKind.TRG_UNIT),
        "buildQueue1": Member("buildQueue1", 0x098, MemberKind.TRG_UNIT),
        "buildQ2": Member("buildQ2", 0x09A, MemberKind.TRG_UNIT),
        "buildQueue2": Member("buildQueue2", 0x09A, MemberKind.TRG_UNIT),
        "buildQ34": Member("buildQ34", 0x09C, MemberKind.DWORD),
        "buildQ3": Member("buildQ3", 0x09C, MemberKind.TRG_UNIT),
        "buildQueue3": Member("buildQueue3", 0x09C, MemberKind.TRG_UNIT),
        "buildQ4": Member("buildQ4", 0x09E, MemberKind.TRG_UNIT),
        "buildQueue4": Member("buildQueue4", 0x09E, MemberKind.TRG_UNIT),
        "buildQ5": Member("buildQ5", 0x0A0, MemberKind.TRG_UNIT),
        "buildQueue5": Member("buildQueue5", 0x0A0, MemberKind.TRG_UNIT),
        "energy": Member("energy", 0x0A2, MemberKind.WORD),
        "buildQueueSlot": Member("buildQueueSlot", 0x0A4, MemberKind.BYTE),
        "uniquenessIdentifier": Member("uniquenessIdentifier", 0x0A5, MemberKind.BYTE),
        "targetOrderSpecial": Member("targetOrderSpecial", 0x0A5, MemberKind.BYTE),
        "secondaryOrder": Member("secondaryOrder", 0x0A6, MemberKind.BYTE),
        "secondaryOrderID": Member("secondaryOrderID", 0x0A6, MemberKind.BYTE),
        "buildingOverlayState": Member("buildingOverlayState", 0x0A7, MemberKind.BYTE),
        "hpGain": Member("hpGain", 0x0A8, MemberKind.WORD),  # buildRepairHpGain
        "shieldGain": Member("shieldGain", 0x0AA, MemberKind.WORD),
        "remainingBuildTime": Member("remainingBuildTime", 0x0AC, MemberKind.WORD),
        "previousHP": Member("previousHP", 0x0AE, MemberKind.WORD),
        # alphaID (StoredUnit)
        "loadedUnitIndex0": Member("loadedUnitIndex0", 0x0B0, MemberKind.WORD),
        "loadedUnitIndex1": Member("loadedUnitIndex1", 0x0B2, MemberKind.WORD),
        "loadedUnitIndex2": Member("loadedUnitIndex2", 0x0B4, MemberKind.WORD),
        "loadedUnitIndex3": Member("loadedUnitIndex3", 0x0B6, MemberKind.WORD),
        "loadedUnitIndex4": Member("loadedUnitIndex4", 0x0B8, MemberKind.WORD),
        "loadedUnitIndex5": Member("loadedUnitIndex5", 0x0BA, MemberKind.WORD),
        "loadedUnitIndex6": Member("loadedUnitIndex6", 0x0BC, MemberKind.WORD),
        "loadedUnitIndex7": Member("loadedUnitIndex7", 0x0BE, MemberKind.WORD),
        # 0x0C0 union, vulture
        "mineCount": Member("mineCount", 0x0C0, MemberKind.BYTE),
        "spiderMineCount": Member("spiderMineCount", 0x0C0, MemberKind.BYTE),
        "pInHanger": Member("pInHanger", 0x0C0, MemberKind.C_UNIT),
        "pOutHanger": Member("pOutHanger", 0x0C4, MemberKind.C_UNIT),
        "inHangerCount": Member("inHangerCount", 0x0C8, MemberKind.BYTE),
        "outHangerCount": Member("outHangerCount", 0x0C9, MemberKind.BYTE),  # carrier
        "parent": Member("parent", 0x0C0, MemberKind.C_UNIT),
        "prevFighter": Member("prevFighter", 0x0C4, MemberKind.C_UNIT),
        "nextFighter": Member("nextFighter", 0x0C8, MemberKind.C_UNIT),
        "inHanger": Member("inHanger", 0x0CC, MemberKind.BOOL),
        "isOutsideHangar": Member("isOutsideHangar", 0x0CC, MemberKind.BOOL),  # fighter
        "_unknown_00": Member("_unknown_00", 0x0C0, MemberKind.DWORD),
        "_unknown_04": Member("_unknown_04", 0x0C4, MemberKind.DWORD),
        "flagSpawnFrame": Member("flagSpawnFrame", 0x0C8, MemberKind.DWORD),  # beacon
        "addon": Member("addon", 0x0C0, MemberKind.C_UNIT),
        "addonBuildType": Member("addonBuildType", 0x0C4, MemberKind.TRG_UNIT),
        "upgradeResearchTime": Member("upgradeResearchTime", 0x0C6, MemberKind.WORD),
        "techType": Member("techType", 0x0C8, MemberKind.TECH),
        "upgradeType": Member("upgradeType", 0x0C9, MemberKind.UPGRADE),
        "larvaTimer": Member("larvaTimer", 0x0CA, MemberKind.BYTE),
        "landingTimer": Member("landingTimer", 0x0CB, MemberKind.BYTE),
        "creepTimer": Member("creepTimer", 0x0CC, MemberKind.BYTE),
        "upgradeLevel": Member("upgradeLevel", 0x0CD, MemberKind.BYTE),
        "__E": Member("__E", 0x0CE, MemberKind.WORD),  # building
        "pPowerup": Member("pPowerup", 0x0C0, MemberKind.C_UNIT),
        "targetResourcePosition": Member("targetResourcePosition", 0x0C4, MemberKind.POSITION),
        "targetResourceX": Member("targetResourceX", 0x0C4, MemberKind.WORD),
        "targetResourceY": Member("targetResourceY", 0x0C6, MemberKind.WORD),
        "targetResourceUnit": Member("targetResourceUnit", 0x0C8, MemberKind.C_UNIT),
        "repairResourceLossTimer": Member("repairResourceLossTimer", 0x0CC, MemberKind.WORD),
        "isCarryingSomething": Member("isCarryingSomething", 0x0CE, MemberKind.BOOL),
        "resourceCarryCount": Member("resourceCarryCount", 0x0CF, MemberKind.BYTE),  # worker
        "resourceCount": Member("resourceCount", 0x0D0, MemberKind.WORD),  # 0x0D0 union
        "resourceIscript": Member("resourceIscript", 0x0D2, MemberKind.BYTE),
        "gatherQueueCount": Member("gatherQueueCount", 0x0D3, MemberKind.BYTE),
        "nextGatherer": Member("nextGatherer", 0x0D4, MemberKind.C_UNIT),
        "resourceGroup": Member("resourceGroup", 0x0D8, MemberKind.BYTE),
        "resourceBelongsToAI": Member("resourceBelongsToAI", 0x0D9, MemberKind.BYTE),
        "nydusExit": Member("nydusExit", 0x0D0, MemberKind.C_UNIT),
        "nukeDot": Member("nukeDot", 0x0D0, MemberKind.C_SPRITE),  # ghost
        "pPowerTemplate": Member("pPowerTemplate", 0x0D0, MemberKind.C_SPRITE),  # Pylon
        "pNuke": Member("pNuke", 0x0D0, MemberKind.C_UNIT),
        "bReady": Member("bReady", 0x0D4, MemberKind.BOOL),  # silo
        "harvestValueLU": Member("harvestValueLU", 0x0D0, MemberKind.DWORD),  # hatchery
        "harvestValueL": Member("harvestValueL", 0x0D0, MemberKind.WORD),
        "harvestValueU": Member("harvestValueU", 0x0D2, MemberKind.WORD),
        "harvestValueRB": Member("harvestValueRB", 0x0D4, MemberKind.DWORD),
        "harvestValueR": Member("harvestValueR", 0x0D4, MemberKind.WORD),
        "harvestValueB": Member("harvestValueB", 0x0D6, MemberKind.WORD),
        "originXY": Member("originXY", 0x0D0, MemberKind.POSITION),
        "origin": Member("origin", 0x0D0, MemberKind.POSITION),
        "originX": Member("originX", 0x0D0, MemberKind.WORD),
        "originY": Member("originY", 0x0D2, MemberKind.WORD),  # powerup
        "harvestTarget": Member("harvestTarget", 0x0D0, MemberKind.C_UNIT),
        "prevHarvestUnit": Member("prevHarvestUnit", 0x0D4, MemberKind.C_UNIT),
        "nextHarvestUnit": Member("nextHarvestUnit", 0x0D8, MemberKind.C_UNIT),  # gatherer
        "statusFlags": Member("statusFlags", 0x0DC, MemberKind.DWORD),
        "resourceType": Member("resourceType", 0x0E0, MemberKind.BYTE),
        "wireframeRandomizer": Member("wireframeRandomizer", 0x0E1, MemberKind.BYTE),
        "secondaryOrderState": Member("secondaryOrderState", 0x0E2, MemberKind.BYTE),
        "recentOrderTimer": Member("recentOrderTimer", 0x0E3, MemberKind.BYTE),
        # which players can detect this unit (cloaked/burrowed)
        "visibilityStatus": Member("visibilityStatus", 0x0E4, MemberKind.DWORD),
        "secondaryOrderPosition": Member("secondaryOrderPosition", 0x0E8, MemberKind.POSITION),
        "secondaryOrderX": Member("secondaryOrderX", 0x0E8, MemberKind.WORD),
        "secondaryOrderY": Member("secondaryOrderY", 0x0EA, MemberKind.WORD),
        "currentBuildUnit": Member("currentBuildUnit", 0x0EC, MemberKind.C_UNIT),
        "previousBurrowedUnit": Member("previousBurrowedUnit", 0x0F0, MemberKind.C_UNIT),
        "nextBurrowedUnit": Member("nextBurrowedUnit", 0x0F4, MemberKind.C_UNIT),
        "rallyXY": Member("rallyXY", 0x0F8, MemberKind.POSITION),
        "rallyPosition": Member("rallyPosition", 0x0F8, MemberKind.POSITION),
        "rallyX": Member("rallyX", 0x0F8, MemberKind.WORD),
        "rallyY": Member("rallyY", 0x0FA, MemberKind.WORD),
        "rallyUnit": Member("rallyUnit", 0x0FC, MemberKind.C_UNIT),
        "prevPsiProvider": Member("prevPsiProvider", 0x0F8, MemberKind.C_UNIT),
        "nextPsiProvider": Member("nextPsiProvider", 0x0FC, MemberKind.C_UNIT),
        "path": Member("path", 0x100, MemberKind.DWORD),
        "pathingCollisionInterval": Member("pathingCollisionInterval", 0x104, MemberKind.BYTE),
        "pathingFlags": Member("pathingFlags", 0x105, MemberKind.BYTE),
        "_unused_0x106": Member("_unused_0x106", 0x106, MemberKind.BYTE),
        "isBeingHealed": Member("isBeingHealed", 0x107, MemberKind.BOOL),
        "contourBoundsLU": Member("contourBoundsLU", 0x108, MemberKind.DWORD),
        "contourBoundsL": Member("contourBoundsL", 0x108, MemberKind.WORD),
        "contourBoundsU": Member("contourBoundsU", 0x10A, MemberKind.WORD),
        "contourBoundsRB": Member("contourBoundsRB", 0x10C, MemberKind.DWORD),
        "contourBoundsR": Member("contourBoundsR", 0x10C, MemberKind.WORD),
        "contourBoundsB": Member("contourBoundsB", 0x10E, MemberKind.WORD),
        # status
        "removeTimer": Member("removeTimer", 0x110, MemberKind.WORD),
        "matrixDamage": Member("matrixDamage", 0x112, MemberKind.WORD),
        "defenseMatrixDamage": Member("defenseMatrixDamage", 0x112, MemberKind.WORD),
        "defensiveMatrixHp": Member("defensiveMatrixHp", 0x112, MemberKind.WORD),
        "matrixTimer": Member("matrixTimer", 0x114, MemberKind.BYTE),
        "defenseMatrixTimer": Member("defenseMatrixTimer", 0x114, MemberKind.BYTE),
        "stimTimer": Member("stimTimer", 0x115, MemberKind.BYTE),
        "ensnareTimer": Member("ensnareTimer", 0x116, MemberKind.BYTE),
        "lockdownTimer": Member("lockdownTimer", 0x117, MemberKind.BYTE),
        "irradiateTimer": Member("irradiateTimer", 0x118, MemberKind.BYTE),
        "stasisTimer": Member("stasisTimer", 0x119, MemberKind.BYTE),
        "plagueTimer": Member("plagueTimer", 0x11A, MemberKind.BYTE),
        "stormTimer": Member("stormTimer", 0x11B, MemberKind.BYTE),
        "isUnderStorm": Member("isUnderStorm", 0x11B, MemberKind.BYTE),
        "irradiatedBy": Member("irradiatedBy", 0x11C, MemberKind.C_UNIT),
        "irradiatePlayerID": Member("irradiatePlayerID", 0x120, MemberKind.BYTE),
        "parasiteFlags": Member("parasiteFlags", 0x121, MemberKind.BYTE),
        "cycleCounter": Member("cycleCounter", 0x122, MemberKind.BYTE),
        "isBlind": Member("isBlind", 0x123, MemberKind.BYTE),
        "blindFlags": Member("blindFlags", 0x123, MemberKind.BYTE),
        "maelstromTimer": Member("maelstromTimer", 0x124, MemberKind.BYTE),
        "_unused_0x125": Member("_unused_0x125", 0x125, MemberKind.BYTE),
        "unusedTimer": Member("unusedTimer", 0x125, MemberKind.BYTE),
        "acidSporeCount": Member("acidSporeCount", 0x126, MemberKind.BYTE),
        "acidSporeTime0": Member("acidSporeTime0", 0x127, MemberKind.BYTE),
        "acidSporeTime1": Member("acidSporeTime1", 0x128, MemberKind.BYTE),
        "acidSporeTime2": Member("acidSporeTime2", 0x129, MemberKind.BYTE),
        "acidSporeTime3": Member("acidSporeTime3", 0x12A, MemberKind.BYTE),
        "acidSporeTime4": Member("acidSporeTime4", 0x12B, MemberKind.BYTE),
        "acidSporeTime5": Member("acidSporeTime5", 0x12C, MemberKind.BYTE),
        "acidSporeTime6": Member("acidSporeTime6", 0x12D, MemberKind.BYTE),
        "acidSporeTime7": Member("acidSporeTime7", 0x12E, MemberKind.BYTE),
        "acidSporeTime8": Member("acidSporeTime8", 0x12F, MemberKind.BYTE),
        "bulletBehaviour3by3AttackSequence": Member(
            "bulletBehaviour3by3AttackSequence", 0x130, MemberKind.WORD
        ),
        "offsetIndex3by3": Member("offsetIndex3by3", 0x130, MemberKind.WORD),
        "_padding_0x132": Member("_padding_0x132", 0x132, MemberKind.WORD),
        "pAI": Member("pAI", 0x134, MemberKind.DWORD),
        "airStrength": Member("airStrength", 0x138, MemberKind.WORD),
        "groundStrength": Member("groundStrength", 0x13A, MemberKind.WORD),
        "finderIndexLeft": Member("finderIndexLeft", 0x13C, MemberKind.DWORD),
        "finderIndexRight": Member("finderIndexRight", 0x140, MemberKind.DWORD),
        "finderIndexTop": Member("finderIndexTop", 0x144, MemberKind.DWORD),
        "finderIndexBottom": Member("finderIndexBottom", 0x148, MemberKind.DWORD),
        "repulseUnknown": Member("repulseUnknown", 0x14C, MemberKind.BYTE),
        "repulseAngle": Member("repulseAngle", 0x14D, MemberKind.BYTE),
        "driftPos": Member("driftPos", 0x14E, MemberKind.WORD),
        "bRepMtxXY": Member("bRepMtxXY", 0x14E, MemberKind.WORD),  # mapsizex / 1.5 max
        "bRepMtxX": Member("bRepMtxX", 0x14E, MemberKind.BYTE),
        "bRepMtxY": Member("bRepMtxY", 0x14F, MemberKind.BYTE),
        "driftPosX": Member("driftPosX", 0x14E, MemberKind.BYTE),
        "driftPosY": Member("driftPosY", 0x14F, MemberKind.BYTE),
    }

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

    def _getptr(self):
        if self._ptr is not None:
            return self._ptr
        return PtrCache(self._epd)

    @property
    def prev(self) -> "CUnit":
        return CUnit.from_read(self._epd)

    @prev.setter
    def prev(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["prev"].write(self._epd, ptr)

    @property
    def next(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["next"].offset // 4)

    @next.setter
    def next(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["next"].write(self._epd, ptr)

    @property
    def hp(self) -> c.EUDVariable:
        return self.members["hp"].read(self._epd)

    @hp.setter
    def hp(self, value) -> None:
        self.members["hp"].write(self._epd, value)

    @property
    def hitPoints(self) -> c.EUDVariable:
        return self.members["hitPoints"].read(self._epd)

    @hitPoints.setter
    def hitPoints(self, value) -> None:
        self.members["hitPoints"].write(self._epd, value)

    @property
    def sprite(self) -> c.EUDVariable:
        return self.members["sprite"].read(self._epd)

    @sprite.setter
    def sprite(self, value) -> None:
        self.members["sprite"].write(self._epd, value)

    @property
    def moveTargetXY(self) -> c.EUDVariable:
        return self.members["moveTargetXY"].read(self._epd)

    @moveTargetXY.setter
    def moveTargetXY(self, value) -> None:
        self.members["moveTargetXY"].write(self._epd, value)

    @property
    def moveTargetPosition(self) -> c.EUDVariable:
        return self.members["moveTargetPosition"].read(self._epd)

    @moveTargetPosition.setter
    def moveTargetPosition(self, value) -> None:
        self.members["moveTargetPosition"].write(self._epd, value)

    @property
    def moveTargetX(self) -> c.EUDVariable:
        return self.members["moveTargetX"].read(self._epd)

    @moveTargetX.setter
    def moveTargetX(self, value) -> None:
        self.members["moveTargetX"].write(self._epd, value)

    @property
    def moveTargetY(self) -> c.EUDVariable:
        return self.members["moveTargetY"].read(self._epd)

    @moveTargetY.setter
    def moveTargetY(self, value) -> None:
        self.members["moveTargetY"].write(self._epd, value)

    @property
    def moveTarget(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["moveTarget"].offset // 4)

    @moveTarget.setter
    def moveTarget(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["moveTarget"].write(self._epd, ptr)

    @property
    def moveTargetUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["moveTargetUnit"].offset // 4)

    @moveTargetUnit.setter
    def moveTargetUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["moveTargetUnit"].write(self._epd, ptr)

    @property
    def nextMovementWaypoint(self) -> c.EUDVariable:
        return self.members["nextMovementWaypoint"].read(self._epd)

    @nextMovementWaypoint.setter
    def nextMovementWaypoint(self, value) -> None:
        self.members["nextMovementWaypoint"].write(self._epd, value)

    @property
    def nextTargetWaypoint(self) -> c.EUDVariable:
        return self.members["nextTargetWaypoint"].read(self._epd)

    @nextTargetWaypoint.setter
    def nextTargetWaypoint(self, value) -> None:
        self.members["nextTargetWaypoint"].write(self._epd, value)

    @property
    def movementFlags(self) -> c.EUDVariable:
        return self.members["movementFlags"].read(self._epd)

    @movementFlags.setter
    def movementFlags(self, value) -> None:
        self.members["movementFlags"].write(self._epd, value)

    @property
    def direction(self) -> c.EUDVariable:
        return self.members["direction"].read(self._epd)

    @direction.setter
    def direction(self, value) -> None:
        self.members["direction"].write(self._epd, value)

    @property
    def currentDirection1(self) -> c.EUDVariable:
        return self.members["currentDirection1"].read(self._epd)

    @currentDirection1.setter
    def currentDirection1(self, value) -> None:
        self.members["currentDirection1"].write(self._epd, value)

    @property
    def flingyTurnRadius(self) -> c.EUDVariable:
        return self.members["flingyTurnRadius"].read(self._epd)

    @flingyTurnRadius.setter
    def flingyTurnRadius(self, value) -> None:
        self.members["flingyTurnRadius"].write(self._epd, value)

    @property
    def flingyTurnSpeed(self) -> c.EUDVariable:
        return self.members["flingyTurnSpeed"].read(self._epd)

    @flingyTurnSpeed.setter
    def flingyTurnSpeed(self, value) -> None:
        self.members["flingyTurnSpeed"].write(self._epd, value)

    @property
    def velocityDirection1(self) -> c.EUDVariable:
        return self.members["velocityDirection1"].read(self._epd)

    @velocityDirection1.setter
    def velocityDirection1(self, value) -> None:
        self.members["velocityDirection1"].write(self._epd, value)

    @property
    def flingyID(self) -> c.EUDVariable:
        return self.members["flingyID"].read(self._epd)

    @flingyID.setter
    def flingyID(self, value) -> None:
        self.members["flingyID"].write(self._epd, value)

    @property
    def _unknown_0x026(self) -> c.EUDVariable:
        return self.members["_unknown_0x026"].read(self._epd)

    @_unknown_0x026.setter
    def _unknown_0x026(self, value) -> None:
        self.members["_unknown_0x026"].write(self._epd, value)

    @property
    def flingyMovementType(self) -> c.EUDVariable:
        return self.members["flingyMovementType"].read(self._epd)

    @flingyMovementType.setter
    def flingyMovementType(self, value) -> None:
        self.members["flingyMovementType"].write(self._epd, value)

    @property
    def pos(self) -> c.EUDVariable:
        return self.members["pos"].read(self._epd)

    @pos.setter
    def pos(self, value) -> None:
        self.members["pos"].write(self._epd, value)

    @property
    def position(self) -> c.EUDVariable:
        return self.members["position"].read(self._epd)

    @position.setter
    def position(self, value) -> None:
        self.members["position"].write(self._epd, value)

    @property
    def posX(self) -> c.EUDVariable:
        return self.members["posX"].read(self._epd)

    @posX.setter
    def posX(self, value) -> None:
        self.members["posX"].write(self._epd, value)

    @property
    def positionX(self) -> c.EUDVariable:
        return self.members["positionX"].read(self._epd)

    @positionX.setter
    def positionX(self, value) -> None:
        self.members["positionX"].write(self._epd, value)

    @property
    def posY(self) -> c.EUDVariable:
        return self.members["posY"].read(self._epd)

    @posY.setter
    def posY(self, value) -> None:
        self.members["posY"].write(self._epd, value)

    @property
    def positionY(self) -> c.EUDVariable:
        return self.members["positionY"].read(self._epd)

    @positionY.setter
    def positionY(self, value) -> None:
        self.members["positionY"].write(self._epd, value)

    @property
    def haltX(self) -> c.EUDVariable:
        return self.members["haltX"].read(self._epd)

    @haltX.setter
    def haltX(self, value) -> None:
        self.members["haltX"].write(self._epd, value)

    @property
    def haltY(self) -> c.EUDVariable:
        return self.members["haltY"].read(self._epd)

    @haltY.setter
    def haltY(self, value) -> None:
        self.members["haltY"].write(self._epd, value)

    @property
    def topSpeed(self) -> c.EUDVariable:
        return self.members["topSpeed"].read(self._epd)

    @topSpeed.setter
    def topSpeed(self, value) -> None:
        self.members["topSpeed"].write(self._epd, value)

    @property
    def flingyTopSpeed(self) -> c.EUDVariable:
        return self.members["flingyTopSpeed"].read(self._epd)

    @flingyTopSpeed.setter
    def flingyTopSpeed(self, value) -> None:
        self.members["flingyTopSpeed"].write(self._epd, value)

    @property
    def current_speed1(self) -> c.EUDVariable:
        return self.members["current_speed1"].read(self._epd)

    @current_speed1.setter
    def current_speed1(self, value) -> None:
        self.members["current_speed1"].write(self._epd, value)

    @property
    def current_speed2(self) -> c.EUDVariable:
        return self.members["current_speed2"].read(self._epd)

    @current_speed2.setter
    def current_speed2(self, value) -> None:
        self.members["current_speed2"].write(self._epd, value)

    @property
    def current_speedX(self) -> c.EUDVariable:
        return self.members["current_speedX"].read(self._epd)

    @current_speedX.setter
    def current_speedX(self, value) -> None:
        self.members["current_speedX"].write(self._epd, value)

    @property
    def current_speedY(self) -> c.EUDVariable:
        return self.members["current_speedY"].read(self._epd)

    @current_speedY.setter
    def current_speedY(self, value) -> None:
        self.members["current_speedY"].write(self._epd, value)

    @property
    def flingyAcceleration(self) -> c.EUDVariable:
        return self.members["flingyAcceleration"].read(self._epd)

    @flingyAcceleration.setter
    def flingyAcceleration(self, value) -> None:
        self.members["flingyAcceleration"].write(self._epd, value)

    @property
    def currentDirection2(self) -> c.EUDVariable:
        return self.members["currentDirection2"].read(self._epd)

    @currentDirection2.setter
    def currentDirection2(self, value) -> None:
        self.members["currentDirection2"].write(self._epd, value)

    @property
    def velocityDirection2(self) -> c.EUDVariable:
        return self.members["velocityDirection2"].read(self._epd)

    @velocityDirection2.setter
    def velocityDirection2(self, value) -> None:
        self.members["velocityDirection2"].write(self._epd, value)

    @property
    def owner(self) -> c.EUDVariable:
        return self.members["owner"].read(self._epd)

    @owner.setter
    def owner(self, value) -> None:
        self.members["owner"].write(self._epd, value)

    @property
    def playerID(self) -> c.EUDVariable:
        return self.members["playerID"].read(self._epd)

    @playerID.setter
    def playerID(self, value) -> None:
        self.members["playerID"].write(self._epd, value)

    @property
    def order(self) -> c.EUDVariable:
        return self.members["order"].read(self._epd)

    @order.setter
    def order(self, value) -> None:
        self.members["order"].write(self._epd, value)

    @property
    def orderID(self) -> c.EUDVariable:
        return self.members["orderID"].read(self._epd)

    @orderID.setter
    def orderID(self, value) -> None:
        self.members["orderID"].write(self._epd, value)

    @property
    def orderState(self) -> c.EUDVariable:
        return self.members["orderState"].read(self._epd)

    @orderState.setter
    def orderState(self, value) -> None:
        self.members["orderState"].write(self._epd, value)

    @property
    def orderSignal(self) -> c.EUDVariable:
        return self.members["orderSignal"].read(self._epd)

    @orderSignal.setter
    def orderSignal(self, value) -> None:
        self.members["orderSignal"].write(self._epd, value)

    @property
    def orderUnitType(self) -> c.EUDVariable:
        return self.members["orderUnitType"].read(self._epd)

    @orderUnitType.setter
    def orderUnitType(self, value) -> None:
        self.members["orderUnitType"].write(self._epd, value)

    @property
    def _unknown_0x052(self) -> c.EUDVariable:
        return self.members["_unknown_0x052"].read(self._epd)

    @_unknown_0x052.setter
    def _unknown_0x052(self, value) -> None:
        self.members["_unknown_0x052"].write(self._epd, value)

    @property
    def cooldown(self) -> c.EUDVariable:
        return self.members["cooldown"].read(self._epd)

    @cooldown.setter
    def cooldown(self, value) -> None:
        self.members["cooldown"].write(self._epd, value)

    @property
    def orderTimer(self) -> c.EUDVariable:
        return self.members["orderTimer"].read(self._epd)

    @orderTimer.setter
    def orderTimer(self, value) -> None:
        self.members["orderTimer"].write(self._epd, value)

    @property
    def mainOrderTimer(self) -> c.EUDVariable:
        return self.members["mainOrderTimer"].read(self._epd)

    @mainOrderTimer.setter
    def mainOrderTimer(self, value) -> None:
        self.members["mainOrderTimer"].write(self._epd, value)

    @property
    def gCooldown(self) -> c.EUDVariable:
        return self.members["gCooldown"].read(self._epd)

    @gCooldown.setter
    def gCooldown(self, value) -> None:
        self.members["gCooldown"].write(self._epd, value)

    @property
    def groundWeaponCooldown(self) -> c.EUDVariable:
        return self.members["groundWeaponCooldown"].read(self._epd)

    @groundWeaponCooldown.setter
    def groundWeaponCooldown(self, value) -> None:
        self.members["groundWeaponCooldown"].write(self._epd, value)

    @property
    def aCooldown(self) -> c.EUDVariable:
        return self.members["aCooldown"].read(self._epd)

    @aCooldown.setter
    def aCooldown(self, value) -> None:
        self.members["aCooldown"].write(self._epd, value)

    @property
    def airWeaponCooldown(self) -> c.EUDVariable:
        return self.members["airWeaponCooldown"].read(self._epd)

    @airWeaponCooldown.setter
    def airWeaponCooldown(self, value) -> None:
        self.members["airWeaponCooldown"].write(self._epd, value)

    @property
    def spellCooldown(self) -> c.EUDVariable:
        return self.members["spellCooldown"].read(self._epd)

    @spellCooldown.setter
    def spellCooldown(self, value) -> None:
        self.members["spellCooldown"].write(self._epd, value)

    @property
    def orderTargetXY(self) -> c.EUDVariable:
        return self.members["orderTargetXY"].read(self._epd)

    @orderTargetXY.setter
    def orderTargetXY(self, value) -> None:
        self.members["orderTargetXY"].write(self._epd, value)

    @property
    def orderTargetPosition(self) -> c.EUDVariable:
        return self.members["orderTargetPosition"].read(self._epd)

    @orderTargetPosition.setter
    def orderTargetPosition(self, value) -> None:
        self.members["orderTargetPosition"].write(self._epd, value)

    @property
    def orderTargetX(self) -> c.EUDVariable:
        return self.members["orderTargetX"].read(self._epd)

    @orderTargetX.setter
    def orderTargetX(self, value) -> None:
        self.members["orderTargetX"].write(self._epd, value)

    @property
    def orderTargetY(self) -> c.EUDVariable:
        return self.members["orderTargetY"].read(self._epd)

    @orderTargetY.setter
    def orderTargetY(self, value) -> None:
        self.members["orderTargetY"].write(self._epd, value)

    @property
    def orderTarget(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["orderTarget"].offset // 4)

    @orderTarget.setter
    def orderTarget(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["orderTarget"].write(self._epd, ptr)

    @property
    def orderTargetUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["orderTargetUnit"].offset // 4)

    @orderTargetUnit.setter
    def orderTargetUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["orderTargetUnit"].write(self._epd, ptr)

    @property
    def shield(self) -> c.EUDVariable:
        return self.members["shield"].read(self._epd)

    @shield.setter
    def shield(self, value) -> None:
        self.members["shield"].write(self._epd, value)

    @property
    def shieldPoints(self) -> c.EUDVariable:
        return self.members["shieldPoints"].read(self._epd)

    @shieldPoints.setter
    def shieldPoints(self, value) -> None:
        self.members["shieldPoints"].write(self._epd, value)

    @property
    def unitId(self) -> c.EUDVariable:
        return self.members["unitId"].read(self._epd)

    @unitId.setter
    def unitId(self, value) -> None:
        self.members["unitId"].write(self._epd, value)

    @property
    def unitType(self) -> c.EUDVariable:
        return self.members["unitType"].read(self._epd)

    @unitType.setter
    def unitType(self, value) -> None:
        self.members["unitType"].write(self._epd, value)

    @property
    def _unknown_0x066(self) -> c.EUDVariable:
        return self.members["_unknown_0x066"].read(self._epd)

    @_unknown_0x066.setter
    def _unknown_0x066(self, value) -> None:
        self.members["_unknown_0x066"].write(self._epd, value)

    @property
    def previousPlayerUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["previousPlayerUnit"].offset // 4)

    @previousPlayerUnit.setter
    def previousPlayerUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["previousPlayerUnit"].write(self._epd, ptr)

    @property
    def nextPlayerUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nextPlayerUnit"].offset // 4)

    @nextPlayerUnit.setter
    def nextPlayerUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nextPlayerUnit"].write(self._epd, ptr)

    @property
    def subUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["subUnit"].offset // 4)

    @subUnit.setter
    def subUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["subUnit"].write(self._epd, ptr)

    @property
    def orderQHead(self) -> c.EUDVariable:
        return self.members["orderQHead"].read(self._epd)

    @orderQHead.setter
    def orderQHead(self, value) -> None:
        self.members["orderQHead"].write(self._epd, value)

    @property
    def orderQueueHead(self) -> c.EUDVariable:
        return self.members["orderQueueHead"].read(self._epd)

    @orderQueueHead.setter
    def orderQueueHead(self, value) -> None:
        self.members["orderQueueHead"].write(self._epd, value)

    @property
    def orderQTail(self) -> c.EUDVariable:
        return self.members["orderQTail"].read(self._epd)

    @orderQTail.setter
    def orderQTail(self, value) -> None:
        self.members["orderQTail"].write(self._epd, value)

    @property
    def orderQueueTail(self) -> c.EUDVariable:
        return self.members["orderQueueTail"].read(self._epd)

    @orderQueueTail.setter
    def orderQueueTail(self, value) -> None:
        self.members["orderQueueTail"].write(self._epd, value)

    @property
    def autoTargetUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["autoTargetUnit"].offset // 4)

    @autoTargetUnit.setter
    def autoTargetUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["autoTargetUnit"].write(self._epd, ptr)

    @property
    def connectedUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["connectedUnit"].offset // 4)

    @connectedUnit.setter
    def connectedUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["connectedUnit"].write(self._epd, ptr)

    @property
    def orderQCount(self) -> c.EUDVariable:
        return self.members["orderQCount"].read(self._epd)

    @orderQCount.setter
    def orderQCount(self, value) -> None:
        self.members["orderQCount"].write(self._epd, value)

    @property
    def orderQueueCount(self) -> c.EUDVariable:
        return self.members["orderQueueCount"].read(self._epd)

    @orderQueueCount.setter
    def orderQueueCount(self, value) -> None:
        self.members["orderQueueCount"].write(self._epd, value)

    @property
    def orderQTimer(self) -> c.EUDVariable:
        return self.members["orderQTimer"].read(self._epd)

    @orderQTimer.setter
    def orderQTimer(self, value) -> None:
        self.members["orderQTimer"].write(self._epd, value)

    @property
    def orderQueueTimer(self) -> c.EUDVariable:
        return self.members["orderQueueTimer"].read(self._epd)

    @orderQueueTimer.setter
    def orderQueueTimer(self, value) -> None:
        self.members["orderQueueTimer"].write(self._epd, value)

    @property
    def _unknown_0x086(self) -> c.EUDVariable:
        return self.members["_unknown_0x086"].read(self._epd)

    @_unknown_0x086.setter
    def _unknown_0x086(self, value) -> None:
        self.members["_unknown_0x086"].write(self._epd, value)

    @property
    def attackNotifyTimer(self) -> c.EUDVariable:
        return self.members["attackNotifyTimer"].read(self._epd)

    @attackNotifyTimer.setter
    def attackNotifyTimer(self, value) -> None:
        self.members["attackNotifyTimer"].write(self._epd, value)

    @property
    def previousUnitType(self) -> c.EUDVariable:
        return self.members["previousUnitType"].read(self._epd)

    @previousUnitType.setter
    def previousUnitType(self, value) -> None:
        self.members["previousUnitType"].write(self._epd, value)

    @property
    def lastEventTimer(self) -> c.EUDVariable:
        return self.members["lastEventTimer"].read(self._epd)

    @lastEventTimer.setter
    def lastEventTimer(self, value) -> None:
        self.members["lastEventTimer"].write(self._epd, value)

    @property
    def lastEventColor(self) -> c.EUDVariable:
        return self.members["lastEventColor"].read(self._epd)

    @lastEventColor.setter
    def lastEventColor(self, value) -> None:
        self.members["lastEventColor"].write(self._epd, value)

    @property
    def _unused_0x08C(self) -> c.EUDVariable:
        return self.members["_unused_0x08C"].read(self._epd)

    @_unused_0x08C.setter
    def _unused_0x08C(self, value) -> None:
        self.members["_unused_0x08C"].write(self._epd, value)

    @property
    def rankIncrease(self) -> c.EUDVariable:
        return self.members["rankIncrease"].read(self._epd)

    @rankIncrease.setter
    def rankIncrease(self, value) -> None:
        self.members["rankIncrease"].write(self._epd, value)

    @property
    def killCount(self) -> c.EUDVariable:
        return self.members["killCount"].read(self._epd)

    @killCount.setter
    def killCount(self, value) -> None:
        self.members["killCount"].write(self._epd, value)

    @property
    def lastAttackingPlayer(self) -> c.EUDVariable:
        return self.members["lastAttackingPlayer"].read(self._epd)

    @lastAttackingPlayer.setter
    def lastAttackingPlayer(self, value) -> None:
        self.members["lastAttackingPlayer"].write(self._epd, value)

    @property
    def secondaryOrderTimer(self) -> c.EUDVariable:
        return self.members["secondaryOrderTimer"].read(self._epd)

    @secondaryOrderTimer.setter
    def secondaryOrderTimer(self, value) -> None:
        self.members["secondaryOrderTimer"].write(self._epd, value)

    @property
    def AIActionFlag(self) -> c.EUDVariable:
        return self.members["AIActionFlag"].read(self._epd)

    @AIActionFlag.setter
    def AIActionFlag(self, value) -> None:
        self.members["AIActionFlag"].write(self._epd, value)

    @property
    def userActionFlags(self) -> c.EUDVariable:
        return self.members["userActionFlags"].read(self._epd)

    @userActionFlags.setter
    def userActionFlags(self, value) -> None:
        self.members["userActionFlags"].write(self._epd, value)

    @property
    def currentButtonSet(self) -> c.EUDVariable:
        return self.members["currentButtonSet"].read(self._epd)

    @currentButtonSet.setter
    def currentButtonSet(self, value) -> None:
        self.members["currentButtonSet"].write(self._epd, value)

    @property
    def isCloaked(self) -> c.EUDVariable:
        return self.members["isCloaked"].read(self._epd)

    @isCloaked.setter
    def isCloaked(self, value) -> None:
        self.members["isCloaked"].write(self._epd, value)

    @property
    def movementState(self) -> c.EUDVariable:
        return self.members["movementState"].read(self._epd)

    @movementState.setter
    def movementState(self, value) -> None:
        self.members["movementState"].write(self._epd, value)

    @property
    def buildQ12(self) -> c.EUDVariable:
        return self.members["buildQ12"].read(self._epd)

    @buildQ12.setter
    def buildQ12(self, value) -> None:
        self.members["buildQ12"].write(self._epd, value)

    @property
    def buildQ1(self) -> c.EUDVariable:
        return self.members["buildQ1"].read(self._epd)

    @buildQ1.setter
    def buildQ1(self, value) -> None:
        self.members["buildQ1"].write(self._epd, value)

    @property
    def buildQueue1(self) -> c.EUDVariable:
        return self.members["buildQueue1"].read(self._epd)

    @buildQueue1.setter
    def buildQueue1(self, value) -> None:
        self.members["buildQueue1"].write(self._epd, value)

    @property
    def buildQ2(self) -> c.EUDVariable:
        return self.members["buildQ2"].read(self._epd)

    @buildQ2.setter
    def buildQ2(self, value) -> None:
        self.members["buildQ2"].write(self._epd, value)

    @property
    def buildQueue2(self) -> c.EUDVariable:
        return self.members["buildQueue2"].read(self._epd)

    @buildQueue2.setter
    def buildQueue2(self, value) -> None:
        self.members["buildQueue2"].write(self._epd, value)

    @property
    def buildQ34(self) -> c.EUDVariable:
        return self.members["buildQ34"].read(self._epd)

    @buildQ34.setter
    def buildQ34(self, value) -> None:
        self.members["buildQ34"].write(self._epd, value)

    @property
    def buildQ3(self) -> c.EUDVariable:
        return self.members["buildQ3"].read(self._epd)

    @buildQ3.setter
    def buildQ3(self, value) -> None:
        self.members["buildQ3"].write(self._epd, value)

    @property
    def buildQueue3(self) -> c.EUDVariable:
        return self.members["buildQueue3"].read(self._epd)

    @buildQueue3.setter
    def buildQueue3(self, value) -> None:
        self.members["buildQueue3"].write(self._epd, value)

    @property
    def buildQ4(self) -> c.EUDVariable:
        return self.members["buildQ4"].read(self._epd)

    @buildQ4.setter
    def buildQ4(self, value) -> None:
        self.members["buildQ4"].write(self._epd, value)

    @property
    def buildQueue4(self) -> c.EUDVariable:
        return self.members["buildQueue4"].read(self._epd)

    @buildQueue4.setter
    def buildQueue4(self, value) -> None:
        self.members["buildQueue4"].write(self._epd, value)

    @property
    def buildQ5(self) -> c.EUDVariable:
        return self.members["buildQ5"].read(self._epd)

    @buildQ5.setter
    def buildQ5(self, value) -> None:
        self.members["buildQ5"].write(self._epd, value)

    @property
    def buildQueue5(self) -> c.EUDVariable:
        return self.members["buildQueue5"].read(self._epd)

    @buildQueue5.setter
    def buildQueue5(self, value) -> None:
        self.members["buildQueue5"].write(self._epd, value)

    @property
    def energy(self) -> c.EUDVariable:
        return self.members["energy"].read(self._epd)

    @energy.setter
    def energy(self, value) -> None:
        self.members["energy"].write(self._epd, value)

    @property
    def buildQueueSlot(self) -> c.EUDVariable:
        return self.members["buildQueueSlot"].read(self._epd)

    @buildQueueSlot.setter
    def buildQueueSlot(self, value) -> None:
        self.members["buildQueueSlot"].write(self._epd, value)

    @property
    def uniquenessIdentifier(self) -> c.EUDVariable:
        return self.members["uniquenessIdentifier"].read(self._epd)

    @uniquenessIdentifier.setter
    def uniquenessIdentifier(self, value) -> None:
        self.members["uniquenessIdentifier"].write(self._epd, value)

    @property
    def targetOrderSpecial(self) -> c.EUDVariable:
        return self.members["targetOrderSpecial"].read(self._epd)

    @targetOrderSpecial.setter
    def targetOrderSpecial(self, value) -> None:
        self.members["targetOrderSpecial"].write(self._epd, value)

    @property
    def secondaryOrder(self) -> c.EUDVariable:
        return self.members["secondaryOrder"].read(self._epd)

    @secondaryOrder.setter
    def secondaryOrder(self, value) -> None:
        self.members["secondaryOrder"].write(self._epd, value)

    @property
    def secondaryOrderID(self) -> c.EUDVariable:
        return self.members["secondaryOrderID"].read(self._epd)

    @secondaryOrderID.setter
    def secondaryOrderID(self, value) -> None:
        self.members["secondaryOrderID"].write(self._epd, value)

    @property
    def buildingOverlayState(self) -> c.EUDVariable:
        return self.members["buildingOverlayState"].read(self._epd)

    @buildingOverlayState.setter
    def buildingOverlayState(self, value) -> None:
        self.members["buildingOverlayState"].write(self._epd, value)

    @property
    def hpGain(self) -> c.EUDVariable:
        return self.members["hpGain"].read(self._epd)

    @hpGain.setter
    def hpGain(self, value) -> None:
        self.members["hpGain"].write(self._epd, value)

    @property
    def shieldGain(self) -> c.EUDVariable:
        return self.members["shieldGain"].read(self._epd)

    @shieldGain.setter
    def shieldGain(self, value) -> None:
        self.members["shieldGain"].write(self._epd, value)

    @property
    def remainingBuildTime(self) -> c.EUDVariable:
        return self.members["remainingBuildTime"].read(self._epd)

    @remainingBuildTime.setter
    def remainingBuildTime(self, value) -> None:
        self.members["remainingBuildTime"].write(self._epd, value)

    @property
    def previousHP(self) -> c.EUDVariable:
        return self.members["previousHP"].read(self._epd)

    @previousHP.setter
    def previousHP(self, value) -> None:
        self.members["previousHP"].write(self._epd, value)

    @property
    def loadedUnitIndex0(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex0"].read(self._epd)

    @loadedUnitIndex0.setter
    def loadedUnitIndex0(self, value) -> None:
        self.members["loadedUnitIndex0"].write(self._epd, value)

    @property
    def loadedUnitIndex1(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex1"].read(self._epd)

    @loadedUnitIndex1.setter
    def loadedUnitIndex1(self, value) -> None:
        self.members["loadedUnitIndex1"].write(self._epd, value)

    @property
    def loadedUnitIndex2(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex2"].read(self._epd)

    @loadedUnitIndex2.setter
    def loadedUnitIndex2(self, value) -> None:
        self.members["loadedUnitIndex2"].write(self._epd, value)

    @property
    def loadedUnitIndex3(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex3"].read(self._epd)

    @loadedUnitIndex3.setter
    def loadedUnitIndex3(self, value) -> None:
        self.members["loadedUnitIndex3"].write(self._epd, value)

    @property
    def loadedUnitIndex4(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex4"].read(self._epd)

    @loadedUnitIndex4.setter
    def loadedUnitIndex4(self, value) -> None:
        self.members["loadedUnitIndex4"].write(self._epd, value)

    @property
    def loadedUnitIndex5(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex5"].read(self._epd)

    @loadedUnitIndex5.setter
    def loadedUnitIndex5(self, value) -> None:
        self.members["loadedUnitIndex5"].write(self._epd, value)

    @property
    def loadedUnitIndex6(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex6"].read(self._epd)

    @loadedUnitIndex6.setter
    def loadedUnitIndex6(self, value) -> None:
        self.members["loadedUnitIndex6"].write(self._epd, value)

    @property
    def loadedUnitIndex7(self) -> c.EUDVariable:
        return self.members["loadedUnitIndex7"].read(self._epd)

    @loadedUnitIndex7.setter
    def loadedUnitIndex7(self, value) -> None:
        self.members["loadedUnitIndex7"].write(self._epd, value)

    @property
    def mineCount(self) -> c.EUDVariable:
        return self.members["mineCount"].read(self._epd)

    @mineCount.setter
    def mineCount(self, value) -> None:
        self.members["mineCount"].write(self._epd, value)

    @property
    def spiderMineCount(self) -> c.EUDVariable:
        return self.members["spiderMineCount"].read(self._epd)

    @spiderMineCount.setter
    def spiderMineCount(self, value) -> None:
        self.members["spiderMineCount"].write(self._epd, value)

    @property
    def pInHanger(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["pInHanger"].offset // 4)

    @pInHanger.setter
    def pInHanger(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["pInHanger"].write(self._epd, ptr)

    @property
    def pOutHanger(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["pOutHanger"].offset // 4)

    @pOutHanger.setter
    def pOutHanger(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["pOutHanger"].write(self._epd, ptr)

    @property
    def inHangerCount(self) -> c.EUDVariable:
        return self.members["inHangerCount"].read(self._epd)

    @inHangerCount.setter
    def inHangerCount(self, value) -> None:
        self.members["inHangerCount"].write(self._epd, value)

    @property
    def outHangerCount(self) -> c.EUDVariable:
        return self.members["outHangerCount"].read(self._epd)

    @outHangerCount.setter
    def outHangerCount(self, value) -> None:
        self.members["outHangerCount"].write(self._epd, value)

    @property
    def parent(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["parent"].offset // 4)

    @parent.setter
    def parent(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["parent"].write(self._epd, ptr)

    @property
    def prevFighter(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["prevFighter"].offset // 4)

    @prevFighter.setter
    def prevFighter(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["prevFighter"].write(self._epd, ptr)

    @property
    def nextFighter(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nextFighter"].offset // 4)

    @nextFighter.setter
    def nextFighter(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nextFighter"].write(self._epd, ptr)

    @property
    def inHanger(self) -> c.EUDVariable:
        return self.members["inHanger"].read(self._epd)

    @inHanger.setter
    def inHanger(self, value) -> None:
        self.members["inHanger"].write(self._epd, value)

    @property
    def isOutsideHangar(self) -> c.EUDVariable:
        return self.members["isOutsideHangar"].read(self._epd)

    @isOutsideHangar.setter
    def isOutsideHangar(self, value) -> None:
        self.members["isOutsideHangar"].write(self._epd, value)

    @property
    def _unknown_00(self) -> c.EUDVariable:
        return self.members["_unknown_00"].read(self._epd)

    @_unknown_00.setter
    def _unknown_00(self, value) -> None:
        self.members["_unknown_00"].write(self._epd, value)

    @property
    def _unknown_04(self) -> c.EUDVariable:
        return self.members["_unknown_04"].read(self._epd)

    @_unknown_04.setter
    def _unknown_04(self, value) -> None:
        self.members["_unknown_04"].write(self._epd, value)

    @property
    def flagSpawnFrame(self) -> c.EUDVariable:
        return self.members["flagSpawnFrame"].read(self._epd)

    @flagSpawnFrame.setter
    def flagSpawnFrame(self, value) -> None:
        self.members["flagSpawnFrame"].write(self._epd, value)

    @property
    def addon(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["addon"].offset // 4)

    @addon.setter
    def addon(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["addon"].write(self._epd, ptr)

    @property
    def addonBuildType(self) -> c.EUDVariable:
        return self.members["addonBuildType"].read(self._epd)

    @addonBuildType.setter
    def addonBuildType(self, value) -> None:
        self.members["addonBuildType"].write(self._epd, value)

    @property
    def upgradeResearchTime(self) -> c.EUDVariable:
        return self.members["upgradeResearchTime"].read(self._epd)

    @upgradeResearchTime.setter
    def upgradeResearchTime(self, value) -> None:
        self.members["upgradeResearchTime"].write(self._epd, value)

    @property
    def techType(self) -> c.EUDVariable:
        return self.members["techType"].read(self._epd)

    @techType.setter
    def techType(self, value) -> None:
        self.members["techType"].write(self._epd, value)

    @property
    def upgradeType(self) -> c.EUDVariable:
        return self.members["upgradeType"].read(self._epd)

    @upgradeType.setter
    def upgradeType(self, value) -> None:
        self.members["upgradeType"].write(self._epd, value)

    @property
    def larvaTimer(self) -> c.EUDVariable:
        return self.members["larvaTimer"].read(self._epd)

    @larvaTimer.setter
    def larvaTimer(self, value) -> None:
        self.members["larvaTimer"].write(self._epd, value)

    @property
    def landingTimer(self) -> c.EUDVariable:
        return self.members["landingTimer"].read(self._epd)

    @landingTimer.setter
    def landingTimer(self, value) -> None:
        self.members["landingTimer"].write(self._epd, value)

    @property
    def creepTimer(self) -> c.EUDVariable:
        return self.members["creepTimer"].read(self._epd)

    @creepTimer.setter
    def creepTimer(self, value) -> None:
        self.members["creepTimer"].write(self._epd, value)

    @property
    def upgradeLevel(self) -> c.EUDVariable:
        return self.members["upgradeLevel"].read(self._epd)

    @upgradeLevel.setter
    def upgradeLevel(self, value) -> None:
        self.members["upgradeLevel"].write(self._epd, value)

    @property
    def __E(self) -> c.EUDVariable:
        return self.members["__E"].read(self._epd)

    @__E.setter
    def __E(self, value) -> None:
        self.members["__E"].write(self._epd, value)

    @property
    def pPowerup(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["pPowerup"].offset // 4)

    @pPowerup.setter
    def pPowerup(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["pPowerup"].write(self._epd, ptr)

    @property
    def targetResourcePosition(self) -> c.EUDVariable:
        return self.members["targetResourcePosition"].read(self._epd)

    @targetResourcePosition.setter
    def targetResourcePosition(self, value) -> None:
        self.members["targetResourcePosition"].write(self._epd, value)

    @property
    def targetResourceX(self) -> c.EUDVariable:
        return self.members["targetResourceX"].read(self._epd)

    @targetResourceX.setter
    def targetResourceX(self, value) -> None:
        self.members["targetResourceX"].write(self._epd, value)

    @property
    def targetResourceY(self) -> c.EUDVariable:
        return self.members["targetResourceY"].read(self._epd)

    @targetResourceY.setter
    def targetResourceY(self, value) -> None:
        self.members["targetResourceY"].write(self._epd, value)

    @property
    def targetResourceUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["targetResourceUnit"].offset // 4)

    @targetResourceUnit.setter
    def targetResourceUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["targetResourceUnit"].write(self._epd, ptr)

    @property
    def repairResourceLossTimer(self) -> c.EUDVariable:
        return self.members["repairResourceLossTimer"].read(self._epd)

    @repairResourceLossTimer.setter
    def repairResourceLossTimer(self, value) -> None:
        self.members["repairResourceLossTimer"].write(self._epd, value)

    @property
    def isCarryingSomething(self) -> c.EUDVariable:
        return self.members["isCarryingSomething"].read(self._epd)

    @isCarryingSomething.setter
    def isCarryingSomething(self, value) -> None:
        self.members["isCarryingSomething"].write(self._epd, value)

    @property
    def resourceCarryCount(self) -> c.EUDVariable:
        return self.members["resourceCarryCount"].read(self._epd)

    @resourceCarryCount.setter
    def resourceCarryCount(self, value) -> None:
        self.members["resourceCarryCount"].write(self._epd, value)

    @property
    def resourceCount(self) -> c.EUDVariable:
        return self.members["resourceCount"].read(self._epd)

    @resourceCount.setter
    def resourceCount(self, value) -> None:
        self.members["resourceCount"].write(self._epd, value)

    @property
    def resourceIscript(self) -> c.EUDVariable:
        return self.members["resourceIscript"].read(self._epd)

    @resourceIscript.setter
    def resourceIscript(self, value) -> None:
        self.members["resourceIscript"].write(self._epd, value)

    @property
    def gatherQueueCount(self) -> c.EUDVariable:
        return self.members["gatherQueueCount"].read(self._epd)

    @gatherQueueCount.setter
    def gatherQueueCount(self, value) -> None:
        self.members["gatherQueueCount"].write(self._epd, value)

    @property
    def nextGatherer(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nextGatherer"].offset // 4)

    @nextGatherer.setter
    def nextGatherer(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nextGatherer"].write(self._epd, ptr)

    @property
    def resourceGroup(self) -> c.EUDVariable:
        return self.members["resourceGroup"].read(self._epd)

    @resourceGroup.setter
    def resourceGroup(self, value) -> None:
        self.members["resourceGroup"].write(self._epd, value)

    @property
    def resourceBelongsToAI(self) -> c.EUDVariable:
        return self.members["resourceBelongsToAI"].read(self._epd)

    @resourceBelongsToAI.setter
    def resourceBelongsToAI(self, value) -> None:
        self.members["resourceBelongsToAI"].write(self._epd, value)

    @property
    def nydusExit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nydusExit"].offset // 4)

    @nydusExit.setter
    def nydusExit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nydusExit"].write(self._epd, ptr)

    @property
    def nukeDot(self) -> c.EUDVariable:
        return self.members["nukeDot"].read(self._epd)

    @nukeDot.setter
    def nukeDot(self, value) -> None:
        self.members["nukeDot"].write(self._epd, value)

    @property
    def pPowerTemplate(self) -> c.EUDVariable:
        return self.members["pPowerTemplate"].read(self._epd)

    @pPowerTemplate.setter
    def pPowerTemplate(self, value) -> None:
        self.members["pPowerTemplate"].write(self._epd, value)

    @property
    def pNuke(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["pNuke"].offset // 4)

    @pNuke.setter
    def pNuke(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["pNuke"].write(self._epd, ptr)

    @property
    def bReady(self) -> c.EUDVariable:
        return self.members["bReady"].read(self._epd)

    @bReady.setter
    def bReady(self, value) -> None:
        self.members["bReady"].write(self._epd, value)

    @property
    def harvestValueLU(self) -> c.EUDVariable:
        return self.members["harvestValueLU"].read(self._epd)

    @harvestValueLU.setter
    def harvestValueLU(self, value) -> None:
        self.members["harvestValueLU"].write(self._epd, value)

    @property
    def harvestValueL(self) -> c.EUDVariable:
        return self.members["harvestValueL"].read(self._epd)

    @harvestValueL.setter
    def harvestValueL(self, value) -> None:
        self.members["harvestValueL"].write(self._epd, value)

    @property
    def harvestValueU(self) -> c.EUDVariable:
        return self.members["harvestValueU"].read(self._epd)

    @harvestValueU.setter
    def harvestValueU(self, value) -> None:
        self.members["harvestValueU"].write(self._epd, value)

    @property
    def harvestValueRB(self) -> c.EUDVariable:
        return self.members["harvestValueRB"].read(self._epd)

    @harvestValueRB.setter
    def harvestValueRB(self, value) -> None:
        self.members["harvestValueRB"].write(self._epd, value)

    @property
    def harvestValueR(self) -> c.EUDVariable:
        return self.members["harvestValueR"].read(self._epd)

    @harvestValueR.setter
    def harvestValueR(self, value) -> None:
        self.members["harvestValueR"].write(self._epd, value)

    @property
    def harvestValueB(self) -> c.EUDVariable:
        return self.members["harvestValueB"].read(self._epd)

    @harvestValueB.setter
    def harvestValueB(self, value) -> None:
        self.members["harvestValueB"].write(self._epd, value)

    @property
    def originXY(self) -> c.EUDVariable:
        return self.members["originXY"].read(self._epd)

    @originXY.setter
    def originXY(self, value) -> None:
        self.members["originXY"].write(self._epd, value)

    @property
    def origin(self) -> c.EUDVariable:
        return self.members["origin"].read(self._epd)

    @origin.setter
    def origin(self, value) -> None:
        self.members["origin"].write(self._epd, value)

    @property
    def originX(self) -> c.EUDVariable:
        return self.members["originX"].read(self._epd)

    @originX.setter
    def originX(self, value) -> None:
        self.members["originX"].write(self._epd, value)

    @property
    def originY(self) -> c.EUDVariable:
        return self.members["originY"].read(self._epd)

    @originY.setter
    def originY(self, value) -> None:
        self.members["originY"].write(self._epd, value)

    @property
    def harvestTarget(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["harvestTarget"].offset // 4)

    @harvestTarget.setter
    def harvestTarget(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["harvestTarget"].write(self._epd, ptr)

    @property
    def prevHarvestUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["prevHarvestUnit"].offset // 4)

    @prevHarvestUnit.setter
    def prevHarvestUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["prevHarvestUnit"].write(self._epd, ptr)

    @property
    def nextHarvestUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nextHarvestUnit"].offset // 4)

    @nextHarvestUnit.setter
    def nextHarvestUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nextHarvestUnit"].write(self._epd, ptr)

    @property
    def statusFlags(self) -> c.EUDVariable:
        return self.members["statusFlags"].read(self._epd)

    @statusFlags.setter
    def statusFlags(self, value) -> None:
        self.members["statusFlags"].write(self._epd, value)

    @property
    def resourceType(self) -> c.EUDVariable:
        return self.members["resourceType"].read(self._epd)

    @resourceType.setter
    def resourceType(self, value) -> None:
        self.members["resourceType"].write(self._epd, value)

    @property
    def wireframeRandomizer(self) -> c.EUDVariable:
        return self.members["wireframeRandomizer"].read(self._epd)

    @wireframeRandomizer.setter
    def wireframeRandomizer(self, value) -> None:
        self.members["wireframeRandomizer"].write(self._epd, value)

    @property
    def secondaryOrderState(self) -> c.EUDVariable:
        return self.members["secondaryOrderState"].read(self._epd)

    @secondaryOrderState.setter
    def secondaryOrderState(self, value) -> None:
        self.members["secondaryOrderState"].write(self._epd, value)

    @property
    def recentOrderTimer(self) -> c.EUDVariable:
        return self.members["recentOrderTimer"].read(self._epd)

    @recentOrderTimer.setter
    def recentOrderTimer(self, value) -> None:
        self.members["recentOrderTimer"].write(self._epd, value)

    @property
    def visibilityStatus(self) -> c.EUDVariable:
        return self.members["visibilityStatus"].read(self._epd)

    @visibilityStatus.setter
    def visibilityStatus(self, value) -> None:
        self.members["visibilityStatus"].write(self._epd, value)

    @property
    def secondaryOrderPosition(self) -> c.EUDVariable:
        return self.members["secondaryOrderPosition"].read(self._epd)

    @secondaryOrderPosition.setter
    def secondaryOrderPosition(self, value) -> None:
        self.members["secondaryOrderPosition"].write(self._epd, value)

    @property
    def secondaryOrderX(self) -> c.EUDVariable:
        return self.members["secondaryOrderX"].read(self._epd)

    @secondaryOrderX.setter
    def secondaryOrderX(self, value) -> None:
        self.members["secondaryOrderX"].write(self._epd, value)

    @property
    def secondaryOrderY(self) -> c.EUDVariable:
        return self.members["secondaryOrderY"].read(self._epd)

    @secondaryOrderY.setter
    def secondaryOrderY(self, value) -> None:
        self.members["secondaryOrderY"].write(self._epd, value)

    @property
    def currentBuildUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["currentBuildUnit"].offset // 4)

    @currentBuildUnit.setter
    def currentBuildUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["currentBuildUnit"].write(self._epd, ptr)

    @property
    def previousBurrowedUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["previousBurrowedUnit"].offset // 4)

    @previousBurrowedUnit.setter
    def previousBurrowedUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["previousBurrowedUnit"].write(self._epd, ptr)

    @property
    def nextBurrowedUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nextBurrowedUnit"].offset // 4)

    @nextBurrowedUnit.setter
    def nextBurrowedUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nextBurrowedUnit"].write(self._epd, ptr)

    @property
    def rallyXY(self) -> c.EUDVariable:
        return self.members["rallyXY"].read(self._epd)

    @rallyXY.setter
    def rallyXY(self, value) -> None:
        self.members["rallyXY"].write(self._epd, value)

    @property
    def rallyPosition(self) -> c.EUDVariable:
        return self.members["rallyPosition"].read(self._epd)

    @rallyPosition.setter
    def rallyPosition(self, value) -> None:
        self.members["rallyPosition"].write(self._epd, value)

    @property
    def rallyX(self) -> c.EUDVariable:
        return self.members["rallyX"].read(self._epd)

    @rallyX.setter
    def rallyX(self, value) -> None:
        self.members["rallyX"].write(self._epd, value)

    @property
    def rallyY(self) -> c.EUDVariable:
        return self.members["rallyY"].read(self._epd)

    @rallyY.setter
    def rallyY(self, value) -> None:
        self.members["rallyY"].write(self._epd, value)

    @property
    def rallyUnit(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["rallyUnit"].offset // 4)

    @rallyUnit.setter
    def rallyUnit(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["rallyUnit"].write(self._epd, ptr)

    @property
    def prevPsiProvider(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["prevPsiProvider"].offset // 4)

    @prevPsiProvider.setter
    def prevPsiProvider(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["prevPsiProvider"].write(self._epd, ptr)

    @property
    def nextPsiProvider(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["nextPsiProvider"].offset // 4)

    @nextPsiProvider.setter
    def nextPsiProvider(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["nextPsiProvider"].write(self._epd, ptr)

    @property
    def path(self) -> c.EUDVariable:
        return self.members["path"].read(self._epd)

    @path.setter
    def path(self, value) -> None:
        self.members["path"].write(self._epd, value)

    @property
    def pathingCollisionInterval(self) -> c.EUDVariable:
        return self.members["pathingCollisionInterval"].read(self._epd)

    @pathingCollisionInterval.setter
    def pathingCollisionInterval(self, value) -> None:
        self.members["pathingCollisionInterval"].write(self._epd, value)

    @property
    def pathingFlags(self) -> c.EUDVariable:
        return self.members["pathingFlags"].read(self._epd)

    @pathingFlags.setter
    def pathingFlags(self, value) -> None:
        self.members["pathingFlags"].write(self._epd, value)

    @property
    def _unused_0x106(self) -> c.EUDVariable:
        return self.members["_unused_0x106"].read(self._epd)

    @_unused_0x106.setter
    def _unused_0x106(self, value) -> None:
        self.members["_unused_0x106"].write(self._epd, value)

    @property
    def isBeingHealed(self) -> c.EUDVariable:
        return self.members["isBeingHealed"].read(self._epd)

    @isBeingHealed.setter
    def isBeingHealed(self, value) -> None:
        self.members["isBeingHealed"].write(self._epd, value)

    @property
    def contourBoundsLU(self) -> c.EUDVariable:
        return self.members["contourBoundsLU"].read(self._epd)

    @contourBoundsLU.setter
    def contourBoundsLU(self, value) -> None:
        self.members["contourBoundsLU"].write(self._epd, value)

    @property
    def contourBoundsL(self) -> c.EUDVariable:
        return self.members["contourBoundsL"].read(self._epd)

    @contourBoundsL.setter
    def contourBoundsL(self, value) -> None:
        self.members["contourBoundsL"].write(self._epd, value)

    @property
    def contourBoundsU(self) -> c.EUDVariable:
        return self.members["contourBoundsU"].read(self._epd)

    @contourBoundsU.setter
    def contourBoundsU(self, value) -> None:
        self.members["contourBoundsU"].write(self._epd, value)

    @property
    def contourBoundsRB(self) -> c.EUDVariable:
        return self.members["contourBoundsRB"].read(self._epd)

    @contourBoundsRB.setter
    def contourBoundsRB(self, value) -> None:
        self.members["contourBoundsRB"].write(self._epd, value)

    @property
    def contourBoundsR(self) -> c.EUDVariable:
        return self.members["contourBoundsR"].read(self._epd)

    @contourBoundsR.setter
    def contourBoundsR(self, value) -> None:
        self.members["contourBoundsR"].write(self._epd, value)

    @property
    def contourBoundsB(self) -> c.EUDVariable:
        return self.members["contourBoundsB"].read(self._epd)

    @contourBoundsB.setter
    def contourBoundsB(self, value) -> None:
        self.members["contourBoundsB"].write(self._epd, value)

    @property
    def removeTimer(self) -> c.EUDVariable:
        return self.members["removeTimer"].read(self._epd)

    @removeTimer.setter
    def removeTimer(self, value) -> None:
        self.members["removeTimer"].write(self._epd, value)

    @property
    def matrixDamage(self) -> c.EUDVariable:
        return self.members["matrixDamage"].read(self._epd)

    @matrixDamage.setter
    def matrixDamage(self, value) -> None:
        self.members["matrixDamage"].write(self._epd, value)

    @property
    def defenseMatrixDamage(self) -> c.EUDVariable:
        return self.members["defenseMatrixDamage"].read(self._epd)

    @defenseMatrixDamage.setter
    def defenseMatrixDamage(self, value) -> None:
        self.members["defenseMatrixDamage"].write(self._epd, value)

    @property
    def defensiveMatrixHp(self) -> c.EUDVariable:
        return self.members["defensiveMatrixHp"].read(self._epd)

    @defensiveMatrixHp.setter
    def defensiveMatrixHp(self, value) -> None:
        self.members["defensiveMatrixHp"].write(self._epd, value)

    @property
    def matrixTimer(self) -> c.EUDVariable:
        return self.members["matrixTimer"].read(self._epd)

    @matrixTimer.setter
    def matrixTimer(self, value) -> None:
        self.members["matrixTimer"].write(self._epd, value)

    @property
    def defenseMatrixTimer(self) -> c.EUDVariable:
        return self.members["defenseMatrixTimer"].read(self._epd)

    @defenseMatrixTimer.setter
    def defenseMatrixTimer(self, value) -> None:
        self.members["defenseMatrixTimer"].write(self._epd, value)

    @property
    def stimTimer(self) -> c.EUDVariable:
        return self.members["stimTimer"].read(self._epd)

    @stimTimer.setter
    def stimTimer(self, value) -> None:
        self.members["stimTimer"].write(self._epd, value)

    @property
    def ensnareTimer(self) -> c.EUDVariable:
        return self.members["ensnareTimer"].read(self._epd)

    @ensnareTimer.setter
    def ensnareTimer(self, value) -> None:
        self.members["ensnareTimer"].write(self._epd, value)

    @property
    def lockdownTimer(self) -> c.EUDVariable:
        return self.members["lockdownTimer"].read(self._epd)

    @lockdownTimer.setter
    def lockdownTimer(self, value) -> None:
        self.members["lockdownTimer"].write(self._epd, value)

    @property
    def irradiateTimer(self) -> c.EUDVariable:
        return self.members["irradiateTimer"].read(self._epd)

    @irradiateTimer.setter
    def irradiateTimer(self, value) -> None:
        self.members["irradiateTimer"].write(self._epd, value)

    @property
    def stasisTimer(self) -> c.EUDVariable:
        return self.members["stasisTimer"].read(self._epd)

    @stasisTimer.setter
    def stasisTimer(self, value) -> None:
        self.members["stasisTimer"].write(self._epd, value)

    @property
    def plagueTimer(self) -> c.EUDVariable:
        return self.members["plagueTimer"].read(self._epd)

    @plagueTimer.setter
    def plagueTimer(self, value) -> None:
        self.members["plagueTimer"].write(self._epd, value)

    @property
    def stormTimer(self) -> c.EUDVariable:
        return self.members["stormTimer"].read(self._epd)

    @stormTimer.setter
    def stormTimer(self, value) -> None:
        self.members["stormTimer"].write(self._epd, value)

    @property
    def isUnderStorm(self) -> c.EUDVariable:
        return self.members["isUnderStorm"].read(self._epd)

    @isUnderStorm.setter
    def isUnderStorm(self, value) -> None:
        self.members["isUnderStorm"].write(self._epd, value)

    @property
    def irradiatedBy(self) -> "CUnit":
        return CUnit.from_read(self._epd + self.members["irradiatedBy"].offset // 4)

    @irradiatedBy.setter
    def irradiatedBy(self, ptr) -> None:
        if isinstance(ptr, CUnit):
            ptr = ptr._getptr()
        self.members["irradiatedBy"].write(self._epd, ptr)

    @property
    def irradiatePlayerID(self) -> c.EUDVariable:
        return self.members["irradiatePlayerID"].read(self._epd)

    @irradiatePlayerID.setter
    def irradiatePlayerID(self, value) -> None:
        self.members["irradiatePlayerID"].write(self._epd, value)

    @property
    def parasiteFlags(self) -> c.EUDVariable:
        return self.members["parasiteFlags"].read(self._epd)

    @parasiteFlags.setter
    def parasiteFlags(self, value) -> None:
        self.members["parasiteFlags"].write(self._epd, value)

    @property
    def cycleCounter(self) -> c.EUDVariable:
        return self.members["cycleCounter"].read(self._epd)

    @cycleCounter.setter
    def cycleCounter(self, value) -> None:
        self.members["cycleCounter"].write(self._epd, value)

    @property
    def isBlind(self) -> c.EUDVariable:
        return self.members["isBlind"].read(self._epd)

    @isBlind.setter
    def isBlind(self, value) -> None:
        self.members["isBlind"].write(self._epd, value)

    @property
    def blindFlags(self) -> c.EUDVariable:
        return self.members["blindFlags"].read(self._epd)

    @blindFlags.setter
    def blindFlags(self, value) -> None:
        self.members["blindFlags"].write(self._epd, value)

    @property
    def maelstromTimer(self) -> c.EUDVariable:
        return self.members["maelstromTimer"].read(self._epd)

    @maelstromTimer.setter
    def maelstromTimer(self, value) -> None:
        self.members["maelstromTimer"].write(self._epd, value)

    @property
    def _unused_0x125(self) -> c.EUDVariable:
        return self.members["_unused_0x125"].read(self._epd)

    @_unused_0x125.setter
    def _unused_0x125(self, value) -> None:
        self.members["_unused_0x125"].write(self._epd, value)

    @property
    def unusedTimer(self) -> c.EUDVariable:
        return self.members["unusedTimer"].read(self._epd)

    @unusedTimer.setter
    def unusedTimer(self, value) -> None:
        self.members["unusedTimer"].write(self._epd, value)

    @property
    def acidSporeCount(self) -> c.EUDVariable:
        return self.members["acidSporeCount"].read(self._epd)

    @acidSporeCount.setter
    def acidSporeCount(self, value) -> None:
        self.members["acidSporeCount"].write(self._epd, value)

    @property
    def acidSporeTime0(self) -> c.EUDVariable:
        return self.members["acidSporeTime0"].read(self._epd)

    @acidSporeTime0.setter
    def acidSporeTime0(self, value) -> None:
        self.members["acidSporeTime0"].write(self._epd, value)

    @property
    def acidSporeTime1(self) -> c.EUDVariable:
        return self.members["acidSporeTime1"].read(self._epd)

    @acidSporeTime1.setter
    def acidSporeTime1(self, value) -> None:
        self.members["acidSporeTime1"].write(self._epd, value)

    @property
    def acidSporeTime2(self) -> c.EUDVariable:
        return self.members["acidSporeTime2"].read(self._epd)

    @acidSporeTime2.setter
    def acidSporeTime2(self, value) -> None:
        self.members["acidSporeTime2"].write(self._epd, value)

    @property
    def acidSporeTime3(self) -> c.EUDVariable:
        return self.members["acidSporeTime3"].read(self._epd)

    @acidSporeTime3.setter
    def acidSporeTime3(self, value) -> None:
        self.members["acidSporeTime3"].write(self._epd, value)

    @property
    def acidSporeTime4(self) -> c.EUDVariable:
        return self.members["acidSporeTime4"].read(self._epd)

    @acidSporeTime4.setter
    def acidSporeTime4(self, value) -> None:
        self.members["acidSporeTime4"].write(self._epd, value)

    @property
    def acidSporeTime5(self) -> c.EUDVariable:
        return self.members["acidSporeTime5"].read(self._epd)

    @acidSporeTime5.setter
    def acidSporeTime5(self, value) -> None:
        self.members["acidSporeTime5"].write(self._epd, value)

    @property
    def acidSporeTime6(self) -> c.EUDVariable:
        return self.members["acidSporeTime6"].read(self._epd)

    @acidSporeTime6.setter
    def acidSporeTime6(self, value) -> None:
        self.members["acidSporeTime6"].write(self._epd, value)

    @property
    def acidSporeTime7(self) -> c.EUDVariable:
        return self.members["acidSporeTime7"].read(self._epd)

    @acidSporeTime7.setter
    def acidSporeTime7(self, value) -> None:
        self.members["acidSporeTime7"].write(self._epd, value)

    @property
    def acidSporeTime8(self) -> c.EUDVariable:
        return self.members["acidSporeTime8"].read(self._epd)

    @acidSporeTime8.setter
    def acidSporeTime8(self, value) -> None:
        self.members["acidSporeTime8"].write(self._epd, value)

    @property
    def bulletBehaviour3by3AttackSequence(self) -> c.EUDVariable:
        return self.members["bulletBehaviour3by3AttackSequence"].read(self._epd)

    @bulletBehaviour3by3AttackSequence.setter
    def bulletBehaviour3by3AttackSequence(self, value) -> None:
        self.members["bulletBehaviour3by3AttackSequence"].write(self._epd, value)

    @property
    def offsetIndex3by3(self) -> c.EUDVariable:
        return self.members["offsetIndex3by3"].read(self._epd)

    @offsetIndex3by3.setter
    def offsetIndex3by3(self, value) -> None:
        self.members["offsetIndex3by3"].write(self._epd, value)

    @property
    def _padding_0x132(self) -> c.EUDVariable:
        return self.members["_padding_0x132"].read(self._epd)

    @_padding_0x132.setter
    def _padding_0x132(self, value) -> None:
        self.members["_padding_0x132"].write(self._epd, value)

    @property
    def pAI(self) -> c.EUDVariable:
        return self.members["pAI"].read(self._epd)

    @pAI.setter
    def pAI(self, value) -> None:
        self.members["pAI"].write(self._epd, value)

    @property
    def airStrength(self) -> c.EUDVariable:
        return self.members["airStrength"].read(self._epd)

    @airStrength.setter
    def airStrength(self, value) -> None:
        self.members["airStrength"].write(self._epd, value)

    @property
    def groundStrength(self) -> c.EUDVariable:
        return self.members["groundStrength"].read(self._epd)

    @groundStrength.setter
    def groundStrength(self, value) -> None:
        self.members["groundStrength"].write(self._epd, value)

    @property
    def finderIndexLeft(self) -> c.EUDVariable:
        return self.members["finderIndexLeft"].read(self._epd)

    @finderIndexLeft.setter
    def finderIndexLeft(self, value) -> None:
        self.members["finderIndexLeft"].write(self._epd, value)

    @property
    def finderIndexRight(self) -> c.EUDVariable:
        return self.members["finderIndexRight"].read(self._epd)

    @finderIndexRight.setter
    def finderIndexRight(self, value) -> None:
        self.members["finderIndexRight"].write(self._epd, value)

    @property
    def finderIndexTop(self) -> c.EUDVariable:
        return self.members["finderIndexTop"].read(self._epd)

    @finderIndexTop.setter
    def finderIndexTop(self, value) -> None:
        self.members["finderIndexTop"].write(self._epd, value)

    @property
    def finderIndexBottom(self) -> c.EUDVariable:
        return self.members["finderIndexBottom"].read(self._epd)

    @finderIndexBottom.setter
    def finderIndexBottom(self, value) -> None:
        self.members["finderIndexBottom"].write(self._epd, value)

    @property
    def repulseUnknown(self) -> c.EUDVariable:
        return self.members["repulseUnknown"].read(self._epd)

    @repulseUnknown.setter
    def repulseUnknown(self, value) -> None:
        self.members["repulseUnknown"].write(self._epd, value)

    @property
    def repulseAngle(self) -> c.EUDVariable:
        return self.members["repulseAngle"].read(self._epd)

    @repulseAngle.setter
    def repulseAngle(self, value) -> None:
        self.members["repulseAngle"].write(self._epd, value)

    @property
    def driftPos(self) -> c.EUDVariable:
        return self.members["driftPos"].read(self._epd)

    @driftPos.setter
    def driftPos(self, value) -> None:
        self.members["driftPos"].write(self._epd, value)

    @property
    def bRepMtxXY(self) -> c.EUDVariable:
        return self.members["bRepMtxXY"].read(self._epd)

    @bRepMtxXY.setter
    def bRepMtxXY(self, value) -> None:
        self.members["bRepMtxXY"].write(self._epd, value)

    @property
    def bRepMtxX(self) -> c.EUDVariable:
        return self.members["bRepMtxX"].read(self._epd)

    @bRepMtxX.setter
    def bRepMtxX(self, value) -> None:
        self.members["bRepMtxX"].write(self._epd, value)

    @property
    def bRepMtxY(self) -> c.EUDVariable:
        return self.members["bRepMtxY"].read(self._epd)

    @bRepMtxY.setter
    def bRepMtxY(self, value) -> None:
        self.members["bRepMtxY"].write(self._epd, value)

    @property
    def driftPosX(self) -> c.EUDVariable:
        return self.members["driftPosX"].read(self._epd)

    @driftPosX.setter
    def driftPosX(self, value) -> None:
        self.members["driftPosX"].write(self._epd, value)

    @property
    def driftPosY(self) -> c.EUDVariable:
        return self.members["driftPosY"].read(self._epd)

    @driftPosY.setter
    def driftPosY(self, value) -> None:
        self.members["driftPosY"].write(self._epd, value)

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
