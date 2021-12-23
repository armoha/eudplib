#!/usr/bin/python
# -*- coding: utf-8 -*-


from .memiof import (
    f_epdread_epd,
    f_dwread_epd,
    f_dwepdread_epd,
    f_wread_epd,
    f_bread_epd,
    f_dwwrite_epd,
    f_wwrite_epd,
    f_bwrite_epd,
    f_posread_epd,
)

from .. import core as c, utils as ut
from ..localize import _

import functools
import traceback

rwdict = {2: (f_wread_epd, f_wwrite_epd), 1: (f_bread_epd, f_bwrite_epd)}


def _checkEPDAddr(epd):
    if c.IsConstExpr(epd) and epd.rlocmode == 4:
        ut.ep_warn(_("EPD check warning. Don't use raw pointer address"))
        traceback.print_stack()


@functools.lru_cache(None)
def EPDOffsetMap(ct):
    addrTable = {}
    for name, offset, size in ct:
        if size not in [4, 2, 1]:
            raise ut.EPError(_("EPDOffsetMap member size should be in 4, 2, 1"))
        if offset % size != 0:
            raise ut.EPError(_("EPDOffsetMap members should be aligned"))
        addrTable[name] = offset, size

    class OffsetMap:
        def __init__(self, epd):
            _checkEPDAddr(epd)

            self._epd = epd

        def __getattr__(self, name):
            offset, size = addrTable[name]
            offsetEPD = offset // 4
            subp = offset % 4
            if size == 4:
                return f_dwread_epd(self._epd + offsetEPD)
            else:
                return rwdict[size][0](self._epd + offsetEPD, subp)

        def getepd(self, name):
            offset, size = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as epd"))
            return f_epdread_epd(self._epd + offset // 4)

        def getdwepd(self, name):
            offset, size = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as epd"))
            return f_dwepdread_epd(self._epd + offset // 4)

        def getpos(self, name):
            offset, size = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as position"))
            return f_posread_epd(self._epd + offset // 4)

        def __setattr__(self, name, value):
            if name == "_epd":
                super().__setattr__(name, value)
                return

            offset, size = addrTable[name]
            offsetEPD = offset // 4
            subp = offset % 4
            if size == 4:
                return f_dwwrite_epd(self._epd + offsetEPD, value)
            else:
                return rwdict[size][1](self._epd + offsetEPD, subp, value)

    return OffsetMap


EPDCUnitMap = EPDOffsetMap(
    (
        ("prev", 0x000, 4),
        ("next", 0x004, 4),
        ("hitPoints", 0x008, 4),
        ("sprite", 0x00C, 4),
        ("moveTargetPosition", 0x010, 4),
        ("moveTargetX", 0x010, 2),
        ("moveTargetY", 0x012, 2),
        ("moveTargetUnit", 0x014, 4),
        ("nextMovementWaypoint", 0x018, 4),
        ("nextTargetWaypoint", 0x01C, 4),
        ("movementFlags", 0x020, 1),
        ("currentDirection1", 0x021, 1),
        ("flingyTurnRadius", 0x022, 1),
        ("velocityDirection1", 0x023, 1),
        ("flingyID", 0x024, 2),
        ("_unknown_0x026", 0x026, 1),
        ("flingyMovementType", 0x027, 1),
        ("position", 0x028, 4),
        ("positionX", 0x028, 2),
        ("positionY", 0x02A, 2),
        ("haltX", 0x02C, 4),
        ("haltY", 0x030, 4),
        ("flingyTopSpeed", 0x034, 4),
        ("current_speed1", 0x038, 4),
        ("current_speed2", 0x03C, 4),
        ("current_speedX", 0x040, 4),
        ("current_speedY", 0x044, 4),
        ("flingyAcceleration", 0x048, 2),
        ("currentDirection2", 0x04A, 1),
        ("velocityDirection2", 0x04B, 1),
        ("playerID", 0x04C, 1),
        ("orderID", 0x04D, 1),
        ("orderState", 0x04E, 1),
        ("orderSignal", 0x04F, 1),
        ("orderUnitType", 0x050, 2),
        ("mainOrderTimer", 0x054, 1),
        ("groundWeaponCooldown", 0x055, 1),
        ("airWeaponCooldown", 0x056, 1),
        ("spellCooldown", 0x057, 1),
        ("orderTargetPosition", 0x058, 4),
        ("orderTargetX", 0x058, 2),
        ("orderTargetY", 0x05A, 2),
        ("orderTargetUnit", 0x05C, 4),
        ("shieldPoints", 0x060, 4),
        ("unitType", 0x064, 2),
        ("previousPlayerUnit", 0x068, 4),
        ("nextPlayerUnit", 0x06C, 4),
        ("subUnit", 0x070, 4),
        ("orderQueueHead", 0x074, 4),
        ("orderQueueTail", 0x078, 4),
        ("autoTargetUnit", 0x07C, 4),
        ("connectedUnit", 0x080, 4),
        ("orderQueueCount", 0x084, 1),
        ("orderQueueTimer", 0x085, 1),
        ("_unknown_0x086", 0x086, 1),
        ("attackNotifyTimer", 0x087, 1),
        ("previousUnitType", 0x088, 2),
        ("lastEventTimer", 0x08A, 1),
        ("lastEventColor", 0x08B, 1),
        ("_unused_0x08C", 0x08C, 2),
        ("rankIncrease", 0x08E, 1),
        ("killCount", 0x08F, 1),
        ("lastAttackingPlayer", 0x090, 1),
        ("secondaryOrderTimer", 0x091, 1),
        ("AIActionFlag", 0x092, 1),
        ("userActionFlags", 0x093, 1),
        ("currentButtonSet", 0x094, 2),
        ("isCloaked", 0x096, 1),
        ("movementState", 0x097, 1),
        ("buildQueue0", 0x098, 2),
        ("buildQueue1", 0x09A, 2),
        ("buildQueue2", 0x09C, 2),
        ("buildQueue3", 0x09E, 2),
        ("buildQueue4", 0x0A0, 2),
        ("energy", 0x0A2, 2),
        ("buildQueueSlot", 0x0A4, 1),
        ("uniquenessIdentifier", 0x0A5, 1),
        ("secondaryOrderID", 0x0A6, 1),
        ("buildingOverlayState", 0x0A7, 1),
        ("hpGain", 0x0A8, 2),
        ("shieldGain", 0x0AA, 2),
        ("remainingBuildTime", 0x0AC, 2),
        ("previousHP", 0x0AE, 2),
        ("loadedUnitIndex0", 0x0B0, 2),
        ("loadedUnitIndex1", 0x0B2, 2),
        ("loadedUnitIndex2", 0x0B4, 2),
        ("loadedUnitIndex3", 0x0B6, 2),
        ("loadedUnitIndex4", 0x0B8, 2),
        ("loadedUnitIndex5", 0x0BA, 2),
        ("loadedUnitIndex6", 0x0BC, 2),
        ("loadedUnitIndex7", 0x0BE, 2),
        ("spiderMineCount", 0x0C0, 1),  # 0x0C0 union, vulture
        ("pInHanger", 0x0C0, 4),
        ("pOutHanger", 0x0C4, 4),
        ("inHangerCount", 0x0C8, 1),
        ("outHangerCount", 0x0C9, 1),  # carrier
        ("parent", 0x0C0, 4),
        ("prevFighter", 0x0C4, 4),
        ("nextFighter", 0x0C8, 4),
        ("inHanger", 0x0CC, 1),  # fighter
        ("_unknown_00", 0x0C0, 4),
        ("_unknown_04", 0x0C4, 4),
        ("flagSpawnFrame", 0x0C8, 4),  # beacon
        ("addon", 0x0C0, 4),
        ("addonBuildType", 0x0C4, 2),
        ("upgradeResearchTime", 0x0C6, 2),
        ("techType", 0x0C8, 1),
        ("upgradeType", 0x0C9, 1),
        ("larvaTimer", 0x0CA, 1),
        ("landingTimer", 0x0CB, 1),
        ("creepTimer", 0x0CC, 1),
        ("upgradeLevel", 0x0CD, 1),
        ("__E", 0x0CE, 2),  # building
        ("pPowerup", 0x0C0, 4),
        ("targetResourcePosition", 0x0C4, 4),
        ("targetResourceX", 0x0C4, 2),
        ("targetResourceY", 0x0C6, 2),
        ("targetResourceUnit", 0x0C8, 4),
        ("repairResourceLossTimer", 0x0CC, 2),
        ("isCarryingSomething", 0x0CE, 1),
        ("resourceCarryCount", 0x0CF, 1),  # worker
        ("resourceCount", 0x0D0, 2),  # 0x0D0 union
        ("resourceIscript", 0x0D2, 1),
        ("gatherQueueCount", 0x0D3, 1),
        ("nextGatherer", 0x0D4, 4),
        ("resourceGroup", 0x0D8, 1),
        ("resourceBelongsToAI", 0x0D9, 1),  # resource
        ("exit", 0x0D0, 4),  # nydus
        ("nukeDot", 0x0D0, 4),  # ghost
        ("pPowerTemplate", 0x0D0, 4),  # Pylon
        ("pNuke", 0x0D0, 4),
        ("bReady", 0x0D4, 1),  # silo
        ("harvestValueLU", 0x0D0, 4),
        ("harvestValueL", 0x0D0, 2),
        ("harvestValueU", 0x0D2, 2),
        ("harvestValueRB", 0x0D4, 4),
        ("harvestValueR", 0x0D4, 2),
        ("harvestValueB", 0x0D6, 2),  # hatchery
        ("origin", 0x0D0, 4),  # powerup
        ("originX", 0x0D0, 2),  # powerup
        ("originY", 0x0D2, 2),  # powerup
        ("harvestTarget", 0x0D0, 4),
        ("prevHarvestUnit", 0x0D4, 4),
        ("nextHarvestUnit", 0x0D8, 4),  # gatherer
        ("statusFlags", 0x0DC, 4),
        ("resourceType", 0x0E0, 1),
        ("wireframeRandomizer", 0x0E1, 1),
        ("secondaryOrderState", 0x0E2, 1),
        ("recentOrderTimer", 0x0E3, 1),
        ("visibilityStatus", 0x0E4, 4),
        ("secondaryOrderPosition", 0x0E8, 4),
        ("secondaryOrderX", 0x0E8, 2),
        ("secondaryOrderY", 0x0EA, 2),
        ("currentBuildUnit", 0x0EC, 4),
        ("previousBurrowedUnit", 0x0F0, 4),
        ("nextBurrowedUnit", 0x0F4, 4),
        ("rallyPosition", 0x0F8, 4),  # 0x0F8 union
        ("rallyX", 0x0F8, 2),  # 0x0F8 union
        ("rallyY", 0x0FA, 2),  # 0x0F8 union
        ("rallyUnit", 0x0FC, 4),  # rally
        ("prevPsiProvider", 0x0F8, 4),
        ("nextPsiProvider", 0x0FC, 4),  # PsiProvider
        ("path", 0x100, 4),
        ("pathingCollisionInterval", 0x104, 1),
        ("pathingFlags", 0x105, 1),
        ("_unused_0x106", 0x106, 1),
        ("isBeingHealed", 0x107, 1),
        ("contourBoundsLU", 0x108, 4),
        ("contourBoundsL", 0x108, 2),
        ("contourBoundsU", 0x10A, 2),
        ("contourBoundsRB", 0x10C, 4),
        ("contourBoundsR", 0x10C, 2),
        ("contourBoundsB", 0x10E, 2),
        ("removeTimer", 0x110, 2),
        ("defenseMatrixDamage", 0x112, 2),
        ("defenseMatrixTimer", 0x114, 1),
        ("stimTimer", 0x115, 1),
        ("ensnareTimer", 0x116, 1),
        ("lockdownTimer", 0x117, 1),
        ("irradiateTimer", 0x118, 1),
        ("stasisTimer", 0x119, 1),
        ("plagueTimer", 0x11A, 1),
        ("stormTimer", 0x11B, 1),
        ("irradiatedBy", 0x11C, 4),
        ("irradiatePlayerID", 0x120, 1),
        ("parasiteFlags", 0x121, 1),
        ("cycleCounter", 0x122, 1),
        ("isBlind", 0x123, 1),
        ("maelstromTimer", 0x124, 1),
        ("_unused_0x125", 0x125, 1),
        ("acidSporeCount", 0x126, 1),
        ("acidSporeTime0", 0x127, 1),
        ("acidSporeTime1", 0x128, 1),
        ("acidSporeTime2", 0x129, 1),
        ("acidSporeTime3", 0x12A, 1),
        ("acidSporeTime4", 0x12B, 1),
        ("acidSporeTime5", 0x12C, 1),
        ("acidSporeTime6", 0x12D, 1),
        ("acidSporeTime7", 0x12E, 1),
        ("acidSporeTime8", 0x12F, 1),
        ("bulletBehaviour3by3AttackSequence", 0x130, 2),
        ("pAI", 0x134, 4),
        ("airStrength", 0x138, 2),
        ("groundStrength", 0x13A, 2),
        ("_repulseUnknown", 0x14C, 1),
        ("repulseAngle", 0x14D, 1),
        ("bRepMtxX", 0x14E, 1),
        ("bRepMtxY", 0x14F, 1),
    )
)
