#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterator

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut
from eudplib.localize import _

from ...offsetmap import CUnit
from ...trigtrg.runtrigtrg import TrigTriggerBegin, TrigTriggerEnd
from ...utils import EPD
from ..memiof import f_bread_cp, f_cunitepdread_epd, f_dwepdread_epd, f_setcurpl2cpcache
from .unlimiterflag import IsUnlimiterOn


def EUDLoopList(header_offset, break_offset=None) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    blockname = "listloop"
    ut.EUDCreateBlock(blockname, header_offset)

    ptr, epd = f_dwepdread_epd(ut.EPD(header_offset))

    if break_offset is not None:
        cs.EUDWhileNot()(ptr == break_offset)
    else:
        cs.EUDWhile()([ptr > 0, ptr <= 0x7FFFFFFF])

    yield ptr, epd
    cs.EUDSetContinuePoint()
    epd += 1
    f_dwepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.ep_assert(ut.EUDPopBlock(blockname)[1] is header_offset, _("listloop mismatch"))


def EUDLoopUnit() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    ut.EUDCreateBlock("unitloop", 0x628430)

    ptr, epd = f_cunitepdread_epd(EPD(0x628430))

    if cs.EUDWhile()(ptr >= 1):
        yield ptr, epd
        cs.EUDSetContinuePoint()
        epd += 1
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.EUDPopBlock("unitloop")


class _UniqueIdentifier(c.EUDObject):
    def GetDataSize(self) -> int:
        return 4 + 336 * 1699

    def WritePayload(self, emitbuffer) -> None:
        emitbuffer.WriteDword(0)
        for _ in range(1699):
            emitbuffer.WriteSpace(332)
            emitbuffer.WriteDword(0xFF)


def EUDLoopNewUnit(
    allowance: int = 2,
) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    ut.ep_assert(isinstance(allowance, int))
    firstUnitPtr = EPD(0x628430)
    ut.EUDCreateBlock("newunitloop", "newlo")
    tos0 = c.EUDLightVariable(0)
    # tos0 << 0

    ptr, epd = f_cunitepdread_epd(firstUnitPtr)
    if cs.EUDWhileNot()(ptr == 0):
        c.VProc(epd, [c.SetMemory(0x6509B0, c.SetTo, 0xA5 // 4), epd.QueueAddTo(EPD(0x6509B0))])
        uniq = f_bread_cp(0, 1)
        uniqueIdentifier = _UniqueIdentifier()
        CheckUnique = c.DeathsX(c.CurrentPlayer, c.Exactly, 0, 0, 0xFF)
        c.VProc(
            uniq,
            [
                c.SetMemory(0x6509B0, c.Add, EPD(uniqueIdentifier) - EPD(0x59CCA8) - 0xA5 // 4),
                uniq.SetDest(EPD(CheckUnique + 8)),
            ],
        )
        if cs.EUDIfNot()(CheckUnique):
            f_setcurpl2cpcache(uniq, uniq.SetDest(c.CurrentPlayer))
            yield ptr, epd
        if cs.EUDElse()():
            tos0 += 1
            cs.EUDBreakIf(tos0.AtLeast(allowance))
        cs.EUDEndIf()
        cs.EUDSetContinuePoint()
        epd += 1
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    f_setcurpl2cpcache([], tos0.SetNumber(0))
    ut.EUDPopBlock("newunitloop")


def EUDLoopNewCUnit(allowance: int = 2) -> Iterator[CUnit]:
    for ptr, epd in EUDLoopNewUnit(allowance):
        yield CUnit(epd, ptr=ptr)


def EUDLoopUnit2() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """
    if IsUnlimiterOn():
        offset, is_dead = 0x4C // 4, c.MemoryXEPD(0, c.Exactly, 0, 0xFF00)
    else:
        offset, is_dead = 0x0C // 4, c.MemoryEPD(0, c.Exactly, 0)
    ptr = c.EUDVariable()
    epd = c.EUDVariable()
    continue_if = c.Forward()
    set_ptr, set_epd = ptr.SetNumber(0), epd.SetNumber(0)

    cs.DoActions(
        ptr.SetNumber(0x59CCA8),
        c.SetMemory(set_ptr + 20, c.SetTo, 0x59CCA8),
        epd.SetNumber(EPD(0x59CCA8)),
        c.SetMemory(is_dead + 4, c.SetTo, EPD(0x59CCA8) + offset),
        c.SetMemory(set_epd + 20, c.SetTo, EPD(0x59CCA8)),
    )
    if cs.EUDWhileNot()(ptr >= 0x59CCA8 + 336 * 1699 + 1):
        whileblock = ut.EUDPeekBlock("whileblock")[1]
        c.PushTriggerScope()
        continue_okay = c.Forward()
        continue_jump = c.RawTrigger(
            nextptr=whileblock["contpoint"],
            actions=c.SetNextPtr(continue_if, continue_okay),
        )
        c.PopTriggerScope()
        continue_if << c.RawTrigger(
            conditions=is_dead,
            actions=c.SetNextPtr(continue_if, continue_jump),
        )
        continue_okay << c.NextTrigger()
        yield ptr, epd

        cs.EUDSetContinuePoint()
        c.RawTrigger(
            nextptr=whileblock["loopstart"],
            actions=[
                c.SetMemory(is_dead + 4, c.Add, 84),
                c.SetMemory(set_ptr + 20, c.Add, 336),
                set_ptr,
                c.SetMemory(set_epd + 20, c.Add, 84),
                set_epd,
            ],
        )
    cs.EUDEndWhile()


def EUDLoopCUnit() -> Iterator[CUnit]:
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """
    for ptr, epd in EUDLoopUnit2():
        yield CUnit(epd, ptr=ptr)


def EUDLoopPlayerUnit(player) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    player = c.EncodePlayer(player)
    first_player_unit = 0x6283F8
    ut.EUDCreateBlock("playerunitloop", first_player_unit)
    ptr, epd = f_cunitepdread_epd(ut.EPD(first_player_unit) + player)

    if cs.EUDWhile()(ptr >= 1):
        next_unit, nextptr = c.Forward(), c.Forward()
        # /*0x06C*/ BW::CUnit*  nextPlayerUnit;
        # f_cunitepdread_epd(epd + 0x6C // 4, ret=[EPD(next_unit) + 5, EPD(next_unit) + 13])
        c.VProc(
            epd,
            [
                c.SetMemory(0x6509B0, c.SetTo, 0x6C // 4),
                epd.QueueAddTo(EPD(0x6509B0)),
                f_cunitepdread_epd._frets[0].SetDest(EPD(next_unit) + 5),
                f_cunitepdread_epd._frets[1].SetDest(EPD(next_unit) + 13),
                c.SetMemory(f_cunitepdread_epd._nptr, c.SetTo, nextptr),
            ],
        )
        c.SetNextTrigger(f_cunitepdread_epd._fstart)
        nextptr << c.NextTrigger()
        yield ptr, epd
        cs.EUDSetContinuePoint()
        cs.DoActions(
            next_unit << ptr.SetNumber(0),
            epd.SetNumber(0),
        )
    cs.EUDEndWhile()

    ut.EUDPopBlock("playerunitloop")


def EUDLoopPlayerCUnit(player) -> Iterator[CUnit]:
    for ptr, epd in EUDLoopPlayerUnit(player):
        yield CUnit(epd, ptr=ptr)


def EUDLoopBullet() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    for ptr, epd in EUDLoopList(0x64DEC4):
        yield ptr, epd


def EUDLoopSprite() -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    y_epd = c.EUDVariable()
    y_epd << ut.EPD(0x629688)

    ut.EUDCreateBlock("spriteloop", "sprlo")

    if cs.EUDWhile()(y_epd < ut.EPD(0x629688) + 256):
        ptr, epd = f_dwepdread_epd(y_epd)
        if cs.EUDWhile()(ptr >= 1):
            yield ptr, epd
            cs.EUDSetContinuePoint()
            epd += 1
            f_dwepdread_epd(epd, ret=[ptr, epd])
        cs.EUDEndWhile()
        y_epd += 1
    cs.EUDEndWhile()

    ut.EUDPopBlock("spriteloop")


def EUDLoopTrigger(player) -> Iterator[tuple[c.EUDVariable, c.EUDVariable]]:
    player = c.EncodePlayer(player)

    tbegin = TrigTriggerBegin(player)
    if cs.EUDIfNot()(tbegin == 0):
        tend = TrigTriggerEnd(player)
        for ptr, epd in EUDLoopList(tbegin, tend):
            yield ptr, epd
    cs.EUDEndIf()
