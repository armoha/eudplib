#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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


from .memiof import (
    f_cunitread_epd,
    f_cunitepdread_epd,
    f_epdcunitread_epd,
    f_spriteread_epd,
    f_spriteepdread_epd,
    f_epdspriteread_epd,
    f_epdread_epd,
    f_dwread_epd,
    f_dwepdread_epd,
    f_wread_epd,
    f_bread_epd,
    f_dwwrite_epd,
    f_wwrite_epd,
    f_bwrite_epd,
    f_posread_epd,
    f_maskread_epd,
    f_maskwrite_epd,
)
from .locf import f_setloc_epd

from .. import core as c, utils as ut, ctrlstru as cs
from ..localize import _

from collections.abc import Mapping, Sequence
import functools
import traceback
from typing import Union

rwdict = {2: (f_wread_epd, f_wwrite_epd), 1: (f_bread_epd, f_bwrite_epd)}


def _checkEPDAddr(epd):
    if c.IsConstExpr(epd) and epd.rlocmode == 4:
        ut.ep_warn(_("EPD check warning. Don't use raw pointer address"))
        traceback.print_stack()


# @functools.lru_cache(None)
def EPDOffsetMap(ct: Mapping[str, Sequence[Union[int, str, type]]]):
    """dictionary of "name": (size, offset) pairs

    size: 1, 2, 4 or bool, "cunit", "sprite", "pos"
    offset: int
    """
    bytesizes = {
        4: 4,
        2: 2,
        1: 1,
        bool: 1,
        "cunit": 4,
        "sprite": 4,
        "pos": 4,
    }

    addrTable = {}
    for name in ct:
        items = ct[name]
        kind, offset = items[0], items[1]
        if kind not in (4, 2, 1, bool, "cunit", "sprite", "pos"):
            raise ut.EPError(_("EPDOffsetMap member size should be in 4, 2, 1"))
        size = bytesizes[kind]
        if offset % size != 0:
            raise ut.EPError(_("EPDOffsetMap members should be aligned"))
        addrTable[name] = (kind, size, offset)

    class OffsetMap:
        def __init__(self, epd):
            _checkEPDAddr(epd)

            self._epd = epd

        def __getattr__(self, name):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            if kind == "cunit":
                return f_cunitepdread_epd(epd)
            if kind == "sprite":
                return f_epdspriteread_epd(epd)
            if size == 4:
                return f_dwread_epd(epd)
            if kind == bool:
                return f_maskread_epd(epd, 1 << (8 * subp))
            return rwdict[size][0](epd, subp)

        def getepd(self, name):
            kind, size, offset = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as epd"))
            epd = self._epd + offset // 4
            if kind == "cunit":
                return f_epdcunitread_epd(epd)
            if kind == "sprite":
                return f_epdspriteread_epd(epd)
            return f_epdread_epd(epd)

        def getdwepd(self, name):
            kind, size, offset = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as epd"))
            epd = self._epd + offset // 4
            if kind == "cunit":
                return f_cunitepdread_epd(epd)
            if kind == "sprite":
                return f_spriteepdread_epd(epd)
            return f_dwepdread_epd(epd)

        def getpos(self, name):
            kind, size, offset = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as position"))
            return f_posread_epd(self._epd + offset // 4)

        def __setattr__(self, name, value):
            if name == "_epd":
                super().__setattr__(name, value)
                return

            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            if size == 4:
                return f_dwwrite_epd(epd, value)
            return rwdict[size][1](epd, subp, value)

    return OffsetMap


class EPDCUnitMap(
    # fmt: off
    EPDOffsetMap({
        "prev": ("cunit", 0x000), "next": ("cunit", 0x004),
        "hp": (4, 0x008), "hitPoints": (4, 0x008),
        "sprite": ("sprite", 0x00C),
        "moveTargetXY": ("pos", 0x010), "moveTargetPosition": ("pos", 0x010),
        "moveTargetX": (2, 0x010), "moveTargetY": (2, 0x012),
        "moveTarget": ("cunit", 0x014), "moveTargetUnit": ("cunit", 0x014),
        "nextMovementWaypoint": ("pos", 0x018),
        "nextTargetWaypoint": ("pos", 0x01C),
        "movementFlags": (1, 0x020),
        "direction": (1, 0x021), "currentDirection1": (1, 0x021),
        "flingyTurnRadius": (1, 0x022),
        "velocityDirection1": (1, 0x023),
        "flingyID": (2, 0x024),
        "_unknown_0x026": (1, 0x026),
        "flingyMovementType": (1, 0x027),
        "pos": ("pos", 0x028), "position": ("pos", 0x028),
        "posX": (2, 0x028), "positionX": (2, 0x028),
        "posY": (2, 0x02A), "positionY": (2, 0x02A),
        "haltX": (4, 0x02C), "haltY": (4, 0x030),
        "topSpeed": (4, 0x034), "flingyTopSpeed": (4, 0x034),
        "current_speed1": (4, 0x038), "current_speed2": (4, 0x03C),
        "current_speedX": (4, 0x040), "current_speedY": (4, 0x044),
        "flingyAcceleration": (2, 0x048),
        "currentDirection2": (1, 0x04A),
        "velocityDirection2": (1, 0x04B),
        "owner": (1, 0x04C), "playerID": (1, 0x04C),
        "order": (1, 0x04D), "orderID": (1, 0x04D),
        "orderState": (1, 0x04E), "orderSignal": (1, 0x04F),
        "orderUnitType": (2, 0x050),
        "cooldown": (4, 0x054),
        "orderTimer": (1, 0x054), "mainOrderTimer": (1, 0x054),
        "gCooldown": (1, 0x055), "groundWeaponCooldown": (1, 0x055),
        "aCooldown": (1, 0x056), "airWeaponCooldown": (1, 0x056),
        "spellCooldown": (1, 0x057),
        "orderTargetXY": ("pos", 0x058), "orderTargetPosition": ("pos", 0x058),
        "orderTargetX": (2, 0x058), "orderTargetY": (2, 0x05A),
        "orderTarget": ("cunit", 0x05C), "orderTargetUnit": ("cunit", 0x05C),
        "shield": (4, 0x060), "shieldPoints": (4, 0x060),
        "unitId": (2, 0x064), "unitType": (2, 0x064),
        "previousPlayerUnit": ("cunit", 0x068),
        "nextPlayerUnit": ("cunit", 0x06C),
        "subUnit": ("cunit", 0x070),
        "orderQHead": (4, 0x074), "orderQueueHead": (4, 0x074),  # COrder
        "orderQTail": (4, 0x078), "orderQueueTail": (4, 0x078),
        "autoTargetUnit": ("cunit", 0x07C),
        "connectedUnit": ("cunit", 0x080),
        "orderQCount": (1, 0x084), "orderQueueCount": (1, 0x084),
        "orderQTimer": (1, 0x085), "orderQueueTimer": (1, 0x085),
        "_unknown_0x086": (1, 0x086),
        "attackNotifyTimer": (1, 0x087),
        "previousUnitType": (2, 0x088),
        "lastEventTimer": (1, 0x08A),
        "lastEventColor": (1, 0x08B),
        "_unused_0x08C": (2, 0x08C),
        "rankIncrease": (1, 0x08E),
        "killCount": (1, 0x08F),
        "lastAttackingPlayer": (1, 0x090),
        "secondaryOrderTimer": (1, 0x091),
        "AIActionFlag": (1, 0x092),
        "userActionFlags": (1, 0x093),
        "currentButtonSet": (2, 0x094),
        "isCloaked": (bool, 0x096),
        "movementState": (1, 0x097),
        "buildQ12": (4, 0x098),
        "buildQ1": (2, 0x098), "buildQueue1": (2, 0x098),
        "buildQ2": (2, 0x09A), "buildQueue2": (2, 0x09A),
        "buildQ34": (4, 0x09C),
        "buildQ3": (2, 0x09C), "buildQueue3": (2, 0x09C),
        "buildQ4": (2, 0x09E), "buildQueue4": (2, 0x09E),
        "buildQ5": (2, 0x0A0), "buildQueue5": (2, 0x0A0),
        "energy": (2, 0x0A2),
        "buildQueueSlot": (1, 0x0A4),
        "uniquenessIdentifier": (1, 0x0A5),
        "secondaryOrder": (1, 0x0A6), "secondaryOrderID": (1, 0x0A6),
        "buildingOverlayState": (1, 0x0A7),
        "hpGain": (2, 0x0A8),
        "shieldGain": (2, 0x0AA),
        "remainingBuildTime": (2, 0x0AC),
        "previousHP": (2, 0x0AE),
        "loadedUnitIndex0": (2, 0x0B0),
        "loadedUnitIndex1": (2, 0x0B2),
        "loadedUnitIndex2": (2, 0x0B4),
        "loadedUnitIndex3": (2, 0x0B6),
        "loadedUnitIndex4": (2, 0x0B8),
        "loadedUnitIndex5": (2, 0x0BA),
        "loadedUnitIndex6": (2, 0x0BC),
        "loadedUnitIndex7": (2, 0x0BE),
        # 0x0C0 union, vulture
        "mineCount": (1, 0x0C0), "spiderMineCount": (1, 0x0C0),
        "pInHanger": ("cunit", 0x0C0),
        "pOutHanger": ("cunit", 0x0C4),
        "inHangerCount": (1, 0x0C8),
        "outHangerCount": (1, 0x0C9),  # carrier
        "parent": ("cunit", 0x0C0),
        "prevFighter": ("cunit", 0x0C4),
        "nextFighter": ("cunit", 0x0C8),
        "inHanger": (bool, 0x0CC),  # fighter
        "_unknown_00": (4, 0x0C0),
        "_unknown_04": (4, 0x0C4),
        "flagSpawnFrame": (4, 0x0C8),  # beacon
        "addon": ("cunit", 0x0C0),
        "addonBuildType": (2, 0x0C4),
        "upgradeResearchTime": (2, 0x0C6),
        "techType": (1, 0x0C8), "upgradeType": (1, 0x0C9),
        "larvaTimer": (1, 0x0CA),
        "landingTimer": (1, 0x0CB),
        "creepTimer": (1, 0x0CC),
        "upgradeLevel": (1, 0x0CD),
        "__E": (2, 0x0CE),  # building
        "pPowerup": ("cunit", 0x0C0),
        "targetResourcePosition": ("pos", 0x0C4),
        "targetResourceX": (2, 0x0C4), "targetResourceY": (2, 0x0C6),
        "targetResourceUnit": ("cunit", 0x0C8),
        "repairResourceLossTimer": (2, 0x0CC),
        "isCarryingSomething": (bool, 0x0CE),
        "resourceCarryCount": (1, 0x0CF),  # worker
        "resourceCount": (2, 0x0D0),  # 0x0D0 union
        "resourceIscript": (1, 0x0D2),
        "gatherQueueCount": (1, 0x0D3),
        "nextGatherer": ("cunit", 0x0D4),
        "resourceGroup": (1, 0x0D8), "resourceBelongsToAI": (1, 0x0D9),
        "exit": ("cunit", 0x0D0), "nydusExit": ("cunit", 0x0D0),
        "nukeDot": ("sprite", 0x0D0),  # ghost
        "pPowerTemplate": ("sprite", 0x0D0),  # Pylon
        "pNuke": ("cunit", 0x0D0),
        "bReady": (bool, 0x0D4),  # silo
        "harvestValueLU": (4, 0x0D0),  # hatchery
        "harvestValueL": (2, 0x0D0), "harvestValueU": (2, 0x0D2),
        "harvestValueRB": (4, 0x0D4),
        "harvestValueR": (2, 0x0D4), "harvestValueB": (2, 0x0D6),
        "originXY": ("pos", 0x0D0), "origin": ("pos", 0x0D0),
        "originX": (2, 0x0D0), "originY": (2, 0x0D2),  # powerup
        "harvestTarget": ("cunit", 0x0D0),
        "prevHarvestUnit": ("cunit", 0x0D4),
        "nextHarvestUnit": ("cunit", 0x0D8),  # gatherer
        "statusFlags": (4, 0x0DC),
        "resourceType": (1, 0x0E0),
        "wireframeRandomizer": (1, 0x0E1),
        "secondaryOrderState": (1, 0x0E2),
        "recentOrderTimer": (1, 0x0E3),
        "visibilityStatus": (4, 0x0E4),
        "secondaryOrderPosition": ("pos", 0x0E8),
        "secondaryOrderX": (2, 0x0E8), "secondaryOrderY": (2, 0x0EA),
        "currentBuildUnit": ("cunit", 0x0EC),
        "previousBurrowedUnit": ("cunit", 0x0F0),
        "nextBurrowedUnit": ("cunit", 0x0F4),
        "rallyXY": ("pos", 0x0F8), "rallyPosition": ("pos", 0x0F8),
        "rallyX": (2, 0x0F8), "rallyY": (2, 0x0FA),
        "rallyUnit": ("cunit", 0x0FC),
        "prevPsiProvider": ("cunit", 0x0F8),
        "nextPsiProvider": ("cunit", 0x0FC),
        "path": (4, 0x100),
        "pathingCollisionInterval": (1, 0x104),
        "pathingFlags": (1, 0x105),
        "_unused_0x106": (1, 0x106),
        "isBeingHealed": (bool, 0x107),
        "contourBoundsLU": (4, 0x108),
        "contourBoundsL": (2, 0x108), "contourBoundsU": (2, 0x10A),
        "contourBoundsRB": (4, 0x10C),
        "contourBoundsR": (2, 0x10C), "contourBoundsB": (2, 0x10E),
        # status
        "removeTimer": (2, 0x110),
        "matrixDamage": (2, 0x112), "defenseMatrixDamage": (2, 0x112),
        "matrixTimer": (1, 0x114), "defenseMatrixTimer": (1, 0x114),
        "stimTimer": (1, 0x115),
        "ensnareTimer": (1, 0x116),
        "lockdownTimer": (1, 0x117),
        "irradiateTimer": (1, 0x118),
        "stasisTimer": (1, 0x119),
        "plagueTimer": (1, 0x11A),
        "stormTimer": (1, 0x11B),
        "irradiatedBy": ("cunit", 0x11C),
        "irradiatePlayerID": (1, 0x120),
        "parasiteFlags": (1, 0x121),
        "cycleCounter": (1, 0x122),
        "isBlind": (bool, 0x123),
        "maelstromTimer": (1, 0x124),
        "_unused_0x125": (1, 0x125),
        "acidSporeCount": (1, 0x126),
        "acidSporeTime0": (1, 0x127),
        "acidSporeTime1": (1, 0x128),
        "acidSporeTime2": (1, 0x129),
        "acidSporeTime3": (1, 0x12A),
        "acidSporeTime4": (1, 0x12B),
        "acidSporeTime5": (1, 0x12C),
        "acidSporeTime6": (1, 0x12D),
        "acidSporeTime7": (1, 0x12E),
        "acidSporeTime8": (1, 0x12F),
        "bulletBehaviour3by3AttackSequence": (2, 0x130),
        "pAI": (4, 0x134),
        "airStrength": (2, 0x138), "groundStrength": (2, 0x13A),
        "_repulseUnknown": (1, 0x14C), "repulseAngle": (1, 0x14D),
        "bRepMtxXY": (2, 0x14E),
        "bRepMtxX": (1, 0x14E), "bRepMtxY": (1, 0x14F),
    })
    # fmt: on
):
    def set_color(self, player):
        player = c.EncodePlayer(player)
        check_sprite = c.Deaths(0, c.Exactly, 0)
        color_epd = c.EUDVariable()
        sprite_epd = self._epd + 0x00C // 4
        c.VProc(sprite_epd, sprite_epd.SetDest(ut.EPD(check_sprite) + 1))
        if cs.EUDIfNot()(check_sprite):
            f_spriteepdread_epd(sprite_epd, ret=[ut.EPD(check_sprite) + 2, color_epd])
        cs.EUDEndIf()
        if cs.EUDIfNot()(color_epd <= 2):
            f_bwrite_epd(color_epd + 2, 2, player)
        cs.EUDEndIf()

    def check_status_flag(self, value, mask=None):
        if mask is None:
            mask = value
        return c.MemoryXEPD(self._epd + 0x0DC // 4, c.Exactly, value, mask)

    def set_status_flag(self, value, mask=None):
        if mask is None:
            mask = value
        f_maskwrite_epd(self._epd + 0x0DC // 4, value, mask)

    def clear_status_flag(self, mask):
        f_maskwrite_epd(self._epd + 0x0DC // 4, 0, mask)

    def reset_buildq(self, Q1=0xE4):
        self.buildQ12 = 0xE40000 + Q1
        self.buildQ34 = 0xE400E4
        self.buildQ5 = 0xE4

    def die(self):
        self.order = 0

    def remove_collision(self):
        self.set_status_flag(0x00A00000)

    def set_invincible(self):
        self.set_status_flag(0x04000000)

    def clear_invincible(self):
        self.clear_status_flag(0x04000000)

    def set_gathering(self):
        self.set_status_flag(0x00800000)

    def clear_gathering(self):
        self.clear_status_flag(0x00800000)

    def set_speed_upgrade(self):
        self.set_status_flag(0x10000000)

    def clear_speed_upgrade(self):
        self.clear_status_flag(0x10000000)

    def set_hallucination(self):
        self.set_status_flag(value=0x40000000, mask=0x40100000)

    def clear_hallucination(self):
        self.set_status_flag(value=0x00100000, mask=0x40100000)

    def power(self):
        self.clear_status_flag(0x00000008)

    def unpower(self):
        self.set_status_flag(0x00000008)

    def set_air(self):
        self.set_status_flag(0x00000004)

    def set_ground(self):
        self.clear_status_flag(0x00000004)

    def set_noclip(self):
        self.set_status_flag(0x00100000)

    def clear_noclip(self):
        self.clear_status_flag(0x00100000)

    def is_dying(self):
        return [self.order == 0, self.sprite >= 1]

    def is_completed(self):
        return self.check_status_flag(0x00000001)

    def is_hallucination(self):
        return self.check_status_flag(0x40000000)

    def is_in_building(self):
        return self.check_status_flag(0x00000020)

    def is_in_transport(self):
        return self.check_status_flag(0x00000040)

    def is_burrowed(self):
        return self.check_status_flag(0x00000010)

    def setloc(self, location):
        f_setloc_epd(location, self._epd + 0x28 // 4)
