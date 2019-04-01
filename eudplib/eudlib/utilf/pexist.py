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

from ..memiof import f_dwread_epd, f_getcurpl, f_setcurpl

from eudplib import core as c, ctrlstru as cs, utils as ut


@c.EUDFunc
def f_playerexist(player):
    """Check if player has not left the game.

    :returns: 1 if player exists, 0 if not.
    """
    pts = 0x51A280

    cs.EUDSwitch(player)
    for p in range(8):
        if cs.EUDSwitchCase()(p):
            if cs.EUDIf()(c.Memory(pts + p * 12 + 8, c.Exactly, ~(pts + p * 12 + 4))):
                c.EUDReturn(0)
            if cs.EUDElse()():
                c.EUDReturn(1)
            cs.EUDEndIf()

    if cs.EUDSwitchDefault()():
        c.EUDReturn(0)
    cs.EUDEndSwitch()


# --------


def EUDLoopPlayer(ptype="Human", force=None, race=None):
    plist = []
    for p in range(8):
        pinfo = c.GetPlayerInfo(p)
        if (ptype is None or pinfo.typestr == ptype) and
           (force is None or pinfo.force == force) and
           (race is None or pinfo.racestr == race):
            plist.append(p)
    ut.EUDCreateBlock("loopplayerblock", None)
    start, end = min(plist), max(plist)

    v = c.EUDVariable()
    v << start
    if cs.EUDWhile()(v <= end):
        for i in range(start, end):
            if i not in plist:
                cs.EUDContinueIf(v == i)
        cs.EUDContinueIfNot(f_playerexist(v))
        yield v
        cs.EUDSetContinuePoint()
        v += 1
    cs.EUDEndWhile()
    ut.EUDPopBlock("loopplayerblock")


# -------


def EUDPlayerLoop():
    def _footer():
        block = {"origcp": f_getcurpl(), "playerv": c.EUDVariable()}
        playerv = block["playerv"]

        playerv << 0
        cs.EUDWhile()(playerv <= 7)
        cs.EUDContinueIfNot(f_playerexist(playerv))
        f_setcurpl(playerv)

        ut.EUDCreateBlock("ploopblock", block)
        return True

    return cs.CtrlStruOpener(_footer)


def EUDEndPlayerLoop():
    block = ut.EUDPopBlock("ploopblock")[1]
    playerv = block["playerv"]
    origcp = block["origcp"]

    if not cs.EUDIsContinuePointSet():
        cs.EUDSetContinuePoint()

    playerv += 1
    cs.EUDEndWhile()
    f_setcurpl(origcp)
