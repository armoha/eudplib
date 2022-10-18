#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk

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

from dataclasses import dataclass

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import trigtrg as tt
from eudplib import utils as ut
from eudplib.localize import _

from ...utils import EPD
from ..memiof import f_cunitepdread_epd, f_dwepdread_epd


@dataclass
class _UnlimiterBool:
    is_unlimiter_on: bool = False


_unlimiter = _UnlimiterBool(is_unlimiter_on=False)


def _turnUnlimiterOn():
    global _unlimiter
    _unlimiter.is_unlimiter_on = True


def _isUnlimiterOn():
    global _unlimiter
    return _unlimiter.is_unlimiter_on


def EUDLoopList(header_offset, break_offset=None):
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


def EUDLoopUnit():
    ut.EUDCreateBlock("unitloop", 0x628430)

    ptr, epd = f_cunitepdread_epd(EPD(0x628430))

    if cs.EUDWhile()(ptr >= 1):
        yield ptr, epd
        cs.EUDSetContinuePoint()
        epd += 1
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.EUDPopBlock("unitloop")


def EUDLoopNewUnit(allowance=2):
    firstUnitPtr = EPD(0x628430)
    ut.EUDCreateBlock("newunitloop", "newlo")
    tos0 = c.EUDLightVariable()
    tos0 << 0

    ptr, epd = f_cunitepdread_epd(firstUnitPtr)
    if cs.EUDWhile()(ptr >= 1):
        epd += 0xA5 // 4
        if cs.EUDIf()(c.MemoryXEPD(epd, c.AtLeast, 0x100, 0xFF00)):
            cs.DoActions(c.SetMemoryXEPD(epd, c.SetTo, 0, 0xFF00), epd.AddNumber(-(0xA5 // 4)))
            yield ptr, epd
        if cs.EUDElse()():
            cs.DoActions(tos0.AddNumber(1), epd.AddNumber(-(0xA5 // 4)))
            cs.EUDBreakIf(tos0.AtLeast(allowance))
        cs.EUDEndIf()
        cs.EUDSetContinuePoint()
        epd += 1
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.EUDPopBlock("newunitloop")


def EUDLoopUnit2():
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """

    offset = 0x4C // 4
    is_dead = c.MemoryXEPD(0, c.Exactly, 0, 0xFF00)
    ptr = c.EUDVariable()
    epd = c.EUDVariable()
    continue_if = c.Forward()
    set_ptr, set_epd = ptr.SetNumber(0), epd.SetNumber(0)

    cs.DoActions(
        ptr.SetNumber(0x59CCA8),
        c.SetMemory(set_ptr + 20, c.SetTo, 0x59CCA8 + 336),
        epd.SetNumber(EPD(0x59CCA8)),
        c.SetMemory(is_dead + 4, c.SetTo, EPD(0x59CCA8) + 0x4C // 4),
        c.SetMemory(set_epd + 20, c.SetTo, EPD(0x59CCA8) + 84),
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
                set_ptr,
                c.SetMemory(set_ptr + 20, c.Add, 336),
                c.SetMemory(is_dead + 4, c.Add, 84),
                set_epd,
                c.SetMemory(set_epd + 20, c.Add, 84),
            ],
        )
    cs.EUDEndWhile()


def EUDLoopPlayerUnit(player):
    player = c.EncodePlayer(player)
    first_player_unit = 0x6283F8
    ut.EUDCreateBlock("playerunitloop", first_player_unit)
    ptr, epd = f_cunitepdread_epd(ut.EPD(first_player_unit) + player)

    if cs.EUDWhile()(ptr >= 1):
        yield ptr, epd
        cs.EUDSetContinuePoint()
        # /*0x06C*/ BW::CUnit*  nextPlayerUnit;
        epd += 0x6C // 4
        f_cunitepdread_epd(epd, ret=[ptr, epd])
    cs.EUDEndWhile()

    ut.EUDPopBlock("playerunitloop")


def EUDLoopBullet():
    for ptr, epd in EUDLoopList(0x64DEC4):
        yield ptr, epd


def EUDLoopSprite():
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


def EUDLoopTrigger(player):
    player = c.EncodePlayer(player)

    tbegin = tt.TrigTriggerBegin(player)
    if cs.EUDIfNot()(tbegin == 0):
        tend = tt.TrigTriggerEnd(player)
        for ptr, epd in EUDLoopList(tbegin, tend):
            yield ptr, epd
    cs.EUDEndIf()
