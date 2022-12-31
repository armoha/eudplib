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

from ..memiof import f_bread_epd, f_dwread_epd

_userp: c.EUDVariable = c.EUDVariable()
_userp_fws: set[tuple] = set()


def _f_inituserplayerid():
    f_bread_epd(ut.EPD(0x512684), 0, ret=[ut.EPD(_userp.getValueAddr())])


def f_getuserplayerid() -> c.EUDVariable:
    return _userp


def IsUserCP() -> c.Condition:
    """Condition: check if CurrentPlayer equals to user player id (local)"""
    fw = c.Forward()
    ret = c.Memory(0x6509B0, c.Exactly, fw)
    fw << UserP_FW(ret, 8)
    return ret


def _action_all(action: c.Action) -> tuple[c.Action, c.Action]:
    fw = c.Forward()
    ret = c.SetMemory(0x6509B0, c.SetTo, fw)
    fw << UserP_FW(ret, 20)
    return ret, action


def DisplayTextAll(text) -> tuple[c.Action, c.Action]:
    """Action: DisplayText for everyone (including observers)"""
    return _action_all(c.DisplayText(text))


def PlayWAVAll(soundpath) -> tuple[c.Action, c.Action]:
    """Action: PlayWAV for everyone (including observers)"""
    return _action_all(c.PlayWAV(soundpath))


def MinimapPingAll(location) -> tuple[c.Action, c.Action]:
    """Action: MinimapPing for everyone (including observers)"""
    return _action_all(c.MinimapPing(location))


def CenterViewAll(location) -> tuple[c.Action, c.Action]:
    """Action: CenterView for everyone (including observers)"""
    return _action_all(c.CenterView(location))


def SetMissionObjectivesAll(text) -> tuple[c.Action, c.Action]:
    """Action: SetMissionObjectives for everyone (including observers)"""
    return _action_all(c.SetMissionObjectives(text))


def TalkingPortraitAll(unit, time) -> tuple[c.Action, c.Action]:
    """Action: TalkingPortrait for everyone (including observers)"""
    return _action_all(c.TalkingPortrait(unit, time))


# NOTE: should we add (Un)MuteUnitSpeechAll?


class UserP_FW(c.ConstExpr):
    def __init__(self, dest, offset):
        super().__init__(self)
        self._initobj = (dest, offset)

    def Evaluate(self):
        _RegisterUserP(*self._initobj)
        return c.toRlocInt(0)


def RCPC_ResetUserP():
    _userp_fws.clear()


c.RegisterCreatePayloadCallback(RCPC_ResetUserP)


def _RegisterUserP(dest, offset):
    _userp_fws.add((dest, offset))


class UserPBuffer(c.EUDObject):
    def __init__(self):
        super().__init__()

    def GetDataSize(self):
        return (len(_userp_fws) + 1) * 4

    def WritePayload(self, pbuf):
        for dest, offset in _userp_fws:
            pbuf.WriteDword(ut.EPD(dest + offset))
        pbuf.WriteDword(0xFFFFFFFF)


def _f_initisusercp():
    """(internal) Initialize IsUserCP."""
    rb = UserPBuffer()
    ptr = c.EUDVariable(ut.EPD(rb))
    userp = f_getuserplayerid()
    write = c.SetDeaths(0, c.SetTo, 0, 0)
    c.VProc(userp, userp.QueueAssignTo(ut.EPD(write) + 5))

    if cs.EUDInfLoop()():
        v = f_dwread_epd(ptr)
        cs.EUDBreakIf(v == 0xFFFFFFFF)
        c.VProc(v, v.SetDest(ut.EPD(write) + 4))
        c.RawTrigger(actions=[write, ptr.AddNumber(1)])

    cs.EUDEndInfLoop()
