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

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import trigtrg as tt
from eudplib import utils as ut

from ..memiof import f_cunitepdread_epd, f_dwepdread_epd

_unlimiter = False


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
    c.SetVariables([ptr, epd], f_dwepdread_epd(epd))
    cs.EUDEndWhile()

    ut.ep_assert(ut.EUDPopBlock(blockname)[1] is header_offset, "listloop mismatch")


def EUDLoopUnit():
    ut.EUDCreateBlock("unitloop", 0x628430)

    ptr, epd = f_cunitepdread_epd(ut.EPD(0x628430))

    if cs.EUDWhile()(ptr >= 1):
        yield ptr, epd
        cs.EUDSetContinuePoint()
        epd += 1
        c.SetVariables([ptr, epd], f_cunitepdread_epd(epd))
    cs.EUDEndWhile()

    ut.EUDPopBlock("unitloop")


def EUDLoopNewUnit(allowance=2):
    firstUnitPtr = ut.EPD(0x628430)
    ut.EUDCreateBlock('newunitloop', 'newlo')
    tos0 = c.EUDLightVariable()
    tos0 << 0

    ptr, epd = f_cunitepdread_epd(firstUnitPtr)
    if cs.EUDWhile()(ptr >= 1):
        epd += 0xA5 // 4
        if cs.EUDIf()(c.MemoryXEPD(epd, c.AtLeast, 0x100, 0xFF00)):
            cs.DoActions([
                c.SetMemoryXEPD(epd, c.SetTo, 0, 0xFF00),
                epd.AddNumber(-(0xA5 // 4)),
            ])
            yield ptr, epd
        if cs.EUDElse()():
            cs.DoActions([
                tos0.AddNumber(1),
                epd.AddNumber(-(0xA5 // 4))
            ])
            cs.EUDBreakIf(tos0.AtLeast(allowance))
        cs.EUDEndIf()
        cs.EUDSetContinuePoint()
        epd += 1
        c.SetVariables([ptr, epd], f_cunitepdread_epd(epd))
    cs.EUDEndWhile()

    ut.EUDPopBlock('newunitloop')


def EUDLoopUnit2():
    """EUDLoopUnit보다 약간? 빠릅니다. 유닛 리스트를 따라가지 않고
    1700개 유닛을 도는 방식으로 작동합니다.
    """
    ptr, epd = c.EUDCreateVariables(2)
    if not _unlimiter:  # orderID가 [0]Die면 없는 유닛으로 판단.
        offset, cont = 0xC // 4, c.MemoryEPD(epd, c.Exactly, 0)
    else:  # Sprite가 0이면 없는 유닛으로 판단.
        offset, cont = 0x4C // 4, c.MemoryXEPD(epd, c.Exactly, 0, 0xFF00)
    cs.DoActions([ptr.SetNumber(0x59CCA8), epd.SetNumber(ut.EPD(0x59CCA8) + offset)])
    if cs.EUDLoopN()(1700):
        cs.EUDContinueIf(cont)
        yield ptr, epd - offset
        cs.EUDSetContinuePoint()
        cs.DoActions([ptr.AddNumber(336), epd.AddNumber(336 // 4)])
    cs.EUDEndLoopN()


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
        c.SetVariables([ptr, epd], f_cunitepdread_epd(epd))
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
            c.SetVariables([ptr, epd], f_dwepdread_epd(epd))
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
