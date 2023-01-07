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


import functools
import traceback
from typing import Any

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from .locf import f_setloc_epd
from .memiof import (
    f_badd_epd,
    f_bread_epd,
    f_bsubtract_epd,
    f_bwrite_epd,
    f_cunitepdread_epd,
    f_cunitread_epd,
    f_dwadd_epd,
    f_dwepdread_epd,
    f_dwread_epd,
    f_dwsubtract_epd,
    f_dwwrite_epd,
    f_epdcunitread_epd,
    f_epdread_epd,
    f_epdspriteread_epd,
    f_maskread_epd,
    f_maskwrite_epd,
    f_posread_epd,
    f_spriteepdread_epd,
    f_spriteread_epd,
    f_wadd_epd,
    f_wread_epd,
    f_wsubtract_epd,
    f_wwrite_epd,
)
from .utilf.unlimiterflag import IsUnlimiterOn

rdict = {1: f_bread_epd, 2: f_wread_epd, 4: lambda epd, _: f_dwread_epd(epd)}
wdict = {
    1: {
        c.SetTo: f_bwrite_epd,
        c.Add: f_badd_epd,
        c.Subtract: f_bsubtract_epd,
    },
    2: {
        c.SetTo: f_wwrite_epd,
        c.Add: f_wadd_epd,
        c.Subtract: f_wsubtract_epd,
    },
    4: {
        c.SetTo: lambda epd, _, value: f_dwwrite_epd(epd, value),
        c.Add: lambda epd, _, value: f_dwadd_epd(epd, value),
        c.Subtract: lambda epd, _, value: f_dwsubtract_epd(epd, value),
    },
}


def _checkEPDAddr(epd):
    if c.IsConstExpr(epd) and epd.rlocmode == 4:
        ut.ep_warn(_("EPD check warning. Don't use raw pointer address"))
        traceback.print_stack()


@functools.lru_cache(None)
def EPDOffsetMap(ct: "tuple[tuple[str, int, int | type | str], ...]"):
    """Tuple of (name, offset, type) pairs

    name: str
    offset: int
    type: 1, 2, 4 or type, "CUnit", "CSprite", "Position"
    (example: bool, TrgPlayer, TrgUnit)
    """
    typemap = {
        4: 4,
        2: 2,
        1: 1,
        bool: 1,
        "CUnit": 4,
        "CSprite": 4,
        "Position": 4,
        "PositionX": 2,
        "PositionY": 2,
        c.Flingy: 2,
        c.TrgPlayer: 1,
        c.TrgUnit: 2,
        c.UnitOrder: 1,
        c.Upgrade: 1,
        c.Tech: 1,
    }

    addrTable = {}
    for name, offset, kind in ct:
        if kind not in typemap:
            raise ut.EPError(_("Invalid EPDOffsetMap member type: {}").format(kind))
        size = typemap[kind]
        if offset % size != 0:
            raise ut.EPError(_("EPDOffsetMap members should be aligned"))
        addrTable[name] = (kind, size, offset)

    class OffsetMap:
        def __init__(self, epd):
            _checkEPDAddr(epd)

            self._epd = epd

        def __getattr__(self, name):
            try:
                kind, size, offset = addrTable[name]
            except KeyError as e:
                raise AttributeError from e
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            if kind == "CUnit":
                return f_cunitepdread_epd(epd)
            if kind == "CSprite":
                return f_epdspriteread_epd(epd)
            if kind == bool:
                return f_maskread_epd(epd, 1 << (8 * subp))
            return rdict[size](epd, subp)

        def getepd(self, name):
            kind, size, offset = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as epd"))
            epd = self._epd + offset // 4
            if kind == "CUnit":
                return f_epdcunitread_epd(epd)
            if kind == "CSprite":
                return f_epdspriteread_epd(epd)
            return f_epdread_epd(epd)

        def getdwepd(self, name):
            kind, size, offset = addrTable[name]
            ut.ep_assert(size == 4, _("Only dword can be read as epd"))
            epd = self._epd + offset // 4
            if kind == "CUnit":
                return f_cunitepdread_epd(epd)
            if kind == "CSprite":
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
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            return wdict[size][c.SetTo](epd, subp, value)

        def iaddattr(self, name, value):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            return wdict[size][c.Add](epd, subp, value)

        # TODO: add operator for Subtract
        def isubtractattr(self, name, value):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            return wdict[size][c.Subtract](epd, subp, value)

        def isubattr(self, name, value):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            return wdict[size][c.Add](epd, subp, -value)

        def imulattr(self, name, value):
            raise AttributeError

        def ifloordivattr(self, name, value):
            raise AttributeError

        def imodattr(self, name, value):
            raise AttributeError

        def ilshiftattr(self, name, value):
            raise AttributeError

        def irshiftattr(self, name, value):
            raise AttributeError

        def ipowattr(self, name, value):
            raise AttributeError

        def iandattr(self, name, value):
            raise AttributeError

        def iorattr(self, name, value):
            raise AttributeError

        def ixorattr(self, name, value):
            raise AttributeError

        # FIXME: Add operator for x[i] = ~x[i]
        def iinvertattr(self, name, value):
            raise AttributeError

        # Attribute comparisons

        def eqattr(self, name, value):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            mask = ((1 << (8 * size)) - 1) << (8 * subp)
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            if subp == 0:
                return c.MemoryXEPD(epd, c.Exactly, value, mask)
            else:
                return c.MemoryXEPD(epd, c.Exactly, c.f_bitlshift(value, 8 * subp), mask)

        def neattr(self, name, value):
            raise AttributeError

        def leattr(self, name, value):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            mask = ((1 << (8 * size)) - 1) << (8 * subp)
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            if subp == 0:
                return c.MemoryXEPD(epd, c.AtMost, value, mask)
            else:
                return c.MemoryXEPD(epd, c.AtMost, c.f_bitlshift(value, 8 * subp), mask)

        def geattr(self, name, value):
            kind, size, offset = addrTable[name]
            offsetEPD, subp = divmod(offset, 4)
            epd = self._epd + offsetEPD
            mask = ((1 << (8 * size)) - 1) << (8 * subp)
            if hasattr(kind, "cast"):
                value = kind.cast(value)
            if subp == 0:
                return c.MemoryXEPD(epd, c.AtLeast, value, mask)
            else:
                return c.MemoryXEPD(epd, c.AtLeast, c.f_bitlshift(value, 8 * subp), mask)

        def ltattr(self, name, value):
            raise AttributeError

        def gtattr(self, name, value):
            raise AttributeError

    return OffsetMap


# fmt: off
# FIXME : Unsupported dynamic base class
_EPDCUnitMap: Any = EPDOffsetMap((
    ("prev", 0x000, "CUnit"), ("next", 0x004, "CUnit"),  # link
    ("hp", 0x008, 4), ("hitPoints", 0x008, 4),  # displayed value is ceil(healthPoints/256)
    ("sprite", 0x00C, "CSprite"),
    ("moveTargetXY", 0x010, "Position"), ("moveTargetPosition", 0x010, "Position"),
    ("moveTargetX", 0x010, "PositionX"), ("moveTargetY", 0x012, "PositionY"),
    ("moveTarget", 0x014, "CUnit"), ("moveTargetUnit", 0x014, "CUnit"),
    # The next way point in the path the unit is following to get to its destination.
    # Equal to moveToPos for air units since they don't need to navigate around buildings.
    ("nextMovementWaypoint", 0x018, "Position"),
    ("nextTargetWaypoint", 0x01C, "Position"),  # The desired position
    ("movementFlags", 0x020, 1),
    ("direction", 0x021, 1), ("currentDirection1", 0x021, 1),  # current direction the unit is facing
    ("flingyTurnRadius", 0x022, 1), ("flingyTurnSpeed", 0x022, 1),
    ("velocityDirection1", 0x023, 1),
    ("flingyID", 0x024, c.Flingy),
    ("_unknown_0x026", 0x026, 1),
    ("flingyMovementType", 0x027, 1),
    ("pos", 0x028, "Position"), ("position", 0x028, "Position"),
    ("posX", 0x028, "PositionX"), ("positionX", 0x028, "PositionX"),
    ("posY", 0x02A, "PositionY"), ("positionY", 0x02A, "PositionY"),
    ("haltX", 0x02C, 4), ("haltY", 0x030, 4),
    ("topSpeed", 0x034, 4), ("flingyTopSpeed", 0x034, 4),
    ("current_speed1", 0x038, 4), ("current_speed2", 0x03C, 4),
    ("current_speedX", 0x040, 4), ("current_speedY", 0x044, 4),
    ("flingyAcceleration", 0x048, 2),
    ("currentDirection2", 0x04A, 1),
    ("velocityDirection2", 0x04B, 1),  # pathing related
    ("owner", 0x04C, c.TrgPlayer), ("playerID", 0x04C, c.TrgPlayer),
    ("order", 0x04D, 1), ("orderID", 0x04D, 1),
    ("orderState", 0x04E, 1), ("orderSignal", 0x04F, 1),
    ("orderUnitType", 0x050, c.TrgUnit),
    ("_unknown_0x052", 0x052, 2),  # 2-byte padding
    ("cooldown", 0x054, 4),
    ("orderTimer", 0x054, 1), ("mainOrderTimer", 0x054, 1),
    ("gCooldown", 0x055, 1), ("groundWeaponCooldown", 0x055, 1),
    ("aCooldown", 0x056, 1), ("airWeaponCooldown", 0x056, 1),
    ("spellCooldown", 0x057, 1),
    ("orderTargetXY", 0x058, "Position"), ("orderTargetPosition", 0x058, "Position"),  # ActionFocus
    ("orderTargetX", 0x058, "PositionX"), ("orderTargetY", 0x05A, "PositionY"),
    ("orderTarget", 0x05C, "CUnit"), ("orderTargetUnit", 0x05C, "CUnit"),
    ("shield", 0x060, 4), ("shieldPoints", 0x060, 4),
    ("unitId", 0x064, c.TrgUnit), ("unitType", 0x064, c.TrgUnit),
    ("_unknown_0x066", 0x066, 2),  # 2-byte padding
    ("previousPlayerUnit", 0x068, "CUnit"),
    ("nextPlayerUnit", 0x06C, "CUnit"),  # player_link
    ("subUnit", 0x070, "CUnit"),
    ("orderQHead", 0x074, 4), ("orderQueueHead", 0x074, 4),  # COrder
    ("orderQTail", 0x078, 4), ("orderQueueTail", 0x078, 4),
    ("autoTargetUnit", 0x07C, "CUnit"),
    ("connectedUnit", 0x080, "CUnit"),  # larva, in-transit, addons
    ("orderQCount", 0x084, 1), ("orderQueueCount", 0x084, 1),
    ("orderQTimer", 0x085, 1), ("orderQueueTimer", 0x085, 1),
    ("_unknown_0x086", 0x086, 1),
    ("attackNotifyTimer", 0x087, 1),
    ("previousUnitType", 0x088, c.TrgUnit),  # zerg buildings while morphing
    ("lastEventTimer", 0x08A, 1),
    ("lastEventColor", 0x08B, 1),  # 17 = was completed (train, morph), 174 = was attacked
    ("_unused_0x08C", 0x08C, 2),
    ("rankIncrease", 0x08E, 1),
    ("killCount", 0x08F, 1),
    ("lastAttackingPlayer", 0x090, c.TrgPlayer),
    ("secondaryOrderTimer", 0x091, 1),
    ("AIActionFlag", 0x092, 1),
    # 2 = issued an order, 3 = interrupted an order, 4 = hide self before death (self-destruct?)
    ("userActionFlags", 0x093, 1),
    ("currentButtonSet", 0x094, 2),
    ("isCloaked", 0x096, bool),
    ("movementState", 0x097, 1),
    ("buildQ12", 0x098, 4),
    ("buildQ1", 0x098, c.TrgUnit), ("buildQueue1", 0x098, c.TrgUnit),
    ("buildQ2", 0x09A, c.TrgUnit), ("buildQueue2", 0x09A, c.TrgUnit),
    ("buildQ34", 0x09C, 4),
    ("buildQ3", 0x09C, c.TrgUnit), ("buildQueue3", 0x09C, c.TrgUnit),
    ("buildQ4", 0x09E, c.TrgUnit), ("buildQueue4", 0x09E, c.TrgUnit),
    ("buildQ5", 0x0A0, c.TrgUnit), ("buildQueue5", 0x0A0, c.TrgUnit),
    ("energy", 0x0A2, 2),
    ("buildQueueSlot", 0x0A4, 1),
    ("uniquenessIdentifier", 0x0A5, 1), ("targetOrderSpecial", 0x0A5, 1),
    ("secondaryOrder", 0x0A6, 1), ("secondaryOrderID", 0x0A6, 1),
    ("buildingOverlayState", 0x0A7, 1),
    ("hpGain", 0x0A8, 2),  # buildRepairHpGain
    ("shieldGain", 0x0AA, 2),
    ("remainingBuildTime", 0x0AC, 2),
    ("previousHP", 0x0AE, 2),
    ("loadedUnitIndex0", 0x0B0, 2),  # alphaID (StoredUnit)
    ("loadedUnitIndex1", 0x0B2, 2),
    ("loadedUnitIndex2", 0x0B4, 2),
    ("loadedUnitIndex3", 0x0B6, 2),
    ("loadedUnitIndex4", 0x0B8, 2),
    ("loadedUnitIndex5", 0x0BA, 2),
    ("loadedUnitIndex6", 0x0BC, 2),
    ("loadedUnitIndex7", 0x0BE, 2),
    # 0x0C0 union, vulture
    ("mineCount", 0x0C0, 1), ("spiderMineCount", 0x0C0, 1),
    ("pInHanger", 0x0C0, "CUnit"),
    ("pOutHanger", 0x0C4, "CUnit"),
    ("inHangerCount", 0x0C8, 1),
    ("outHangerCount", 0x0C9, 1),  # carrier
    ("parent", 0x0C0, "CUnit"),
    ("prevFighter", 0x0C4, "CUnit"),
    ("nextFighter", 0x0C8, "CUnit"),
    ("inHanger", 0x0CC, bool), ("isOutsideHangar", 0x0CC, bool),  # fighter
    ("_unknown_00", 0x0C0, 4),
    ("_unknown_04", 0x0C4, 4),
    ("flagSpawnFrame", 0x0C8, 4),  # beacon
    ("addon", 0x0C0, "CUnit"),
    ("addonBuildType", 0x0C4, c.TrgUnit),
    ("upgradeResearchTime", 0x0C6, 2),
    ("techType", 0x0C8, c.Tech), ("upgradeType", 0x0C9, c.Upgrade),
    ("larvaTimer", 0x0CA, 1),
    ("landingTimer", 0x0CB, 1),
    ("creepTimer", 0x0CC, 1),
    ("upgradeLevel", 0x0CD, 1),
    ("__E", 0x0CE, 2),  # building
    ("pPowerup", 0x0C0, "CUnit"),
    ("targetResourcePosition", 0x0C4, "Position"),
    ("targetResourceX", 0x0C4, 2), ("targetResourceY", 0x0C6, 2),
    ("targetResourceUnit", 0x0C8, "CUnit"),
    ("repairResourceLossTimer", 0x0CC, 2),
    ("isCarryingSomething", 0x0CE, bool),
    ("resourceCarryCount", 0x0CF, 1),  # worker
    ("resourceCount", 0x0D0, 2),  # 0x0D0 union
    ("resourceIscript", 0x0D2, 1),
    ("gatherQueueCount", 0x0D3, 1),
    ("nextGatherer", 0x0D4, "CUnit"),
    ("resourceGroup", 0x0D8, 1), ("resourceBelongsToAI", 0x0D9, 1),
    ("exit", 0x0D0, "CUnit"), ("nydusExit", 0x0D0, "CUnit"),
    ("nukeDot", 0x0D0, "CSprite"),  # ghost
    ("pPowerTemplate", 0x0D0, "CSprite"),  # Pylon
    ("pNuke", 0x0D0, "CUnit"),
    ("bReady", 0x0D4, bool),  # silo
    ("harvestValueLU", 0x0D0, 4),  # hatchery
    ("harvestValueL", 0x0D0, 2), ("harvestValueU", 0x0D2, 2),
    ("harvestValueRB", 0x0D4, 4),
    ("harvestValueR", 0x0D4, 2), ("harvestValueB", 0x0D6, 2),
    ("originXY", 0x0D0, "Position"), ("origin", 0x0D0, "Position"),
    ("originX", 0x0D0, 2), ("originY", 0x0D2, 2),  # powerup
    ("harvestTarget", 0x0D0, "CUnit"),
    ("prevHarvestUnit", 0x0D4, "CUnit"),
    ("nextHarvestUnit", 0x0D8, "CUnit"),  # gatherer
    ("statusFlags", 0x0DC, 4),
    ("resourceType", 0x0E0, 1),
    ("wireframeRandomizer", 0x0E1, 1),
    ("secondaryOrderState", 0x0E2, 1),
    ("recentOrderTimer", 0x0E3, 1),
    ("visibilityStatus", 0x0E4, 4),  # which players can detect this unit (cloaked/burrowed)
    ("secondaryOrderPosition", 0x0E8, "Position"),
    ("secondaryOrderX", 0x0E8, 2), ("secondaryOrderY", 0x0EA, 2),
    ("currentBuildUnit", 0x0EC, "CUnit"),
    ("previousBurrowedUnit", 0x0F0, "CUnit"),
    ("nextBurrowedUnit", 0x0F4, "CUnit"),
    ("rallyXY", 0x0F8, "Position"), ("rallyPosition", 0x0F8, "Position"),
    ("rallyX", 0x0F8, 2), ("rallyY", 0x0FA, 2),
    ("rallyUnit", 0x0FC, "CUnit"),
    ("prevPsiProvider", 0x0F8, "CUnit"),
    ("nextPsiProvider", 0x0FC, "CUnit"),
    ("path", 0x100, 4),
    ("pathingCollisionInterval", 0x104, 1),
    ("pathingFlags", 0x105, 1),
    ("_unused_0x106", 0x106, 1),
    ("isBeingHealed", 0x107, bool),
    ("contourBoundsLU", 0x108, 4),
    ("contourBoundsL", 0x108, 2), ("contourBoundsU", 0x10A, 2),
    ("contourBoundsRB", 0x10C, 4),
    ("contourBoundsR", 0x10C, 2), ("contourBoundsB", 0x10E, 2),
    # status
    ("removeTimer", 0x110, 2),
    ("matrixDamage", 0x112, 2), ("defenseMatrixDamage", 0x112, 2), ("defensiveMatrixHp", 0x112, 2),
    ("matrixTimer", 0x114, 1), ("defenseMatrixTimer", 0x114, 1),
    ("stimTimer", 0x115, 1),
    ("ensnareTimer", 0x116, 1),
    ("lockdownTimer", 0x117, 1),
    ("irradiateTimer", 0x118, 1),
    ("stasisTimer", 0x119, 1),
    ("plagueTimer", 0x11A, 1),
    ("stormTimer", 0x11B, 1), ("isUnderStorm", 0x11B, 1),
    ("irradiatedBy", 0x11C, "CUnit"),
    ("irradiatePlayerID", 0x120, 1),
    ("parasiteFlags", 0x121, 1),
    ("cycleCounter", 0x122, 1),
    ("isBlind", 0x123, 1), ("blindFlags", 0x123, 1),
    ("maelstromTimer", 0x124, 1),
    ("_unused_0x125", 0x125, 1), ("unusedTimer", 0x125, 1),
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
    ("bulletBehaviour3by3AttackSequence", 0x130, 2), ("offsetIndex3by3", 0x130, 2),
    ("_padding_0x132", 0x132, 2),
    ("pAI", 0x134, 4),
    ("airStrength", 0x138, 2), ("groundStrength", 0x13A, 2),
    ("finderIndexLeft", 0x13C, 4),
    ("finderIndexRight", 0x140, 4),
    ("finderIndexTop", 0x144, 4),
    ("finderIndexBottom", 0x148, 4),
    ("repulseUnknown", 0x14C, 1), ("repulseAngle", 0x14D, 1),
    ("driftPos", 0x14E, 2), ("bRepMtxXY", 0x14E, 2),  # mapsizex / 1.5 max
    ("bRepMtxX", 0x14E, 1), ("bRepMtxY", 0x14F, 1),
    ("driftPosX", 0x14E, 1), ("driftPosY", 0x14F, 1),
))
# fmt: on


class EPDCUnitMap(_EPDCUnitMap):
    def set_color(self, player):
        player = c.EncodePlayer(player)
        check_sprite = c.Deaths(0, c.Exactly, 0, 0)
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
        ut.ep_assert(not IsUnlimiterOn(), "Can't detect unit dying with [unlimiter]")
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
