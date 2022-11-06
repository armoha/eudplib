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
from eudplib import utils as ut

from ...core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from ...core.variable.evcommon import _ev
from ...localize import _
from ..memiof import f_dwread_epd, f_getcurpl, f_setcurpl

_check_playerexist = c.Db(4)


@_EUDPredefineParam((ut.EPD(_check_playerexist),))
@_EUDPredefineReturn(1, 2)
@c.EUDTypedFunc([c.TrgPlayer])
def _playerexist(player):
    """Check if player has not left the game.

    :returns: 1 if player exists, 0 if not.
    """
    pts = 0x51A280
    _ev[1] << 1
    cs.EPDSwitch(ut.EPD(_check_playerexist))
    for p in ut.RandList(range(8)):
        if cs.EUDSwitchCase()(p):
            c.RawTrigger(
                conditions=c.Memory(pts + p * 12 + 8, c.Exactly, ~(pts + p * 12 + 4)),
                actions=_ev[1].SetNumber(0),
            )
    if cs.EUDSwitchDefault()():
        _ev[1] << 0
    cs.EUDEndSwitch()


def f_playerexist(player, *, _cf={}, **kwargs):
    """Check if player has not left the game.

    :returns: 1 if player exists, 0 if not.
    """
    if c.IsEUDVariable(player):
        return _playerexist(player, **kwargs)
    else:
        p = c.EncodePlayer(player)
        ret = kwargs["ret"][0] if "ret" in kwargs else c.EUDVariable()
        if p not in _cf:
            c.PushTriggerScope()
            pts = 0x51A280
            _cf[p] = c.RawTrigger(
                conditions=c.Memory(pts + p * 12 + 8, c.Exactly, ~(pts + p * 12 + 4)),
                actions=c.SetMemoryEPD(0, c.SetTo, 0),
            )
            c.PopTriggerScope()

        nptr = c.Forward()
        c.RawTrigger(
            nextptr=_cf[p],
            actions=[
                ret.SetNumber(1),
                c.SetNextPtr(_cf[p], nptr),
                c.SetMemory(_cf[p] + 344, c.SetTo, ut.EPD(ret.getValueAddr())),
            ],
        )
        nptr << c.NextTrigger()
        return ret


# --------


def EUDLoopPlayer(ptype="Human", force=None, race=None):
    def EncodeForce(f):
        force_dict = {c.Force1: 0, c.Force2: 1, c.Force3: 2, c.Force4: 3}
        if type(f) != int and f in force_dict:
            return force_dict[f]
        return f

    plist = []
    for p in range(8):
        pinfo = c.GetPlayerInfo(p)
        if (
            (not ptype or pinfo.typestr == ptype)
            and (not force or pinfo.force == EncodeForce(force))
            and (not race or pinfo.racestr == race)
        ):
            plist.append(p)
    ut.EUDCreateBlock("loopplayerblock", None)
    if not plist:
        errmsg = _("No player met condition for input map settings:")
        if ptype:
            errmsg += _(" type {}").format(ptype)
        if force:
            errmsg += _(" force {}").format(force)
        if race:
            errmsg += _(" race {}").format(race)
        errmsg += "\n" + _("Check out whether Start Locations are placed correctly.")
        raise ut.EPError(errmsg)
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
