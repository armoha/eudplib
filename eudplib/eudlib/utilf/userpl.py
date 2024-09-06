#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing_extensions import Self

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ...memio import f_bread_epd, f_dwread_epd
from ...offsetmap.scdata import TrgPlayer

_userp: TrgPlayer = TrgPlayer.cast(c.EUDVariable())
_userp_fws: set[tuple] = set()


def _f_inituserplayerid():
    f_bread_epd(ut.EPD(0x512684), 0, ret=[ut.EPD(_userp.getValueAddr())])


def f_getuserplayerid() -> TrgPlayer:
    return _userp


def IsUserCP() -> c.Condition:  # noqa: N802
    """Condition: check if CurrentPlayer equals to user player id (local)"""
    fw = c.Forward()
    ret = c.Memory(0x6509B0, c.Exactly, fw)
    fw << _UserPFw(ret, 8)
    return ret


def _action_all(action: c.Action) -> tuple[c.Action, c.Action]:
    fw = c.Forward()
    ret = c.SetMemory(0x6509B0, c.SetTo, fw)
    fw << _UserPFw(ret, 20)
    return ret, action


def DisplayTextAll(text) -> tuple[c.Action, c.Action]:  # noqa: N802
    """Action: DisplayText for everyone (including observers)"""
    return _action_all(c.DisplayText(text))


def PlayWAVAll(soundpath) -> tuple[c.Action, c.Action]:  # noqa: N802
    """Action: PlayWAV for everyone (including observers)"""
    return _action_all(c.PlayWAV(soundpath))


def MinimapPingAll(location) -> tuple[c.Action, c.Action]:  # noqa: N802
    """Action: MinimapPing for everyone (including observers)"""
    return _action_all(c.MinimapPing(location))


def CenterViewAll(location) -> tuple[c.Action, c.Action]:  # noqa: N802
    """Action: CenterView for everyone (including observers)"""
    return _action_all(c.CenterView(location))


def SetMissionObjectivesAll(text) -> tuple[c.Action, c.Action]:  # noqa: N802
    """Action: SetMissionObjectives for everyone (including observers)"""
    return _action_all(c.SetMissionObjectives(text))


def TalkingPortraitAll(unit, time) -> tuple[c.Action, c.Action]:  # noqa: N802
    """Action: TalkingPortrait for everyone (including observers)"""
    return _action_all(c.TalkingPortrait(unit, time))


# NOTE: should we add (Un)MuteUnitSpeechAll?


class _UserPFw(c.ConstExpr):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(self, dest, offset) -> None:
        super().__init__()
        self._initobj = (dest, offset)

    def Evaluate(self):  # noqa: N802
        _register_userp(*self._initobj)
        return c.toRlocInt(0)


def _rcpc_reset_userp():
    _userp_fws.clear()


c.RegisterCreatePayloadCallback(_rcpc_reset_userp)


def _register_userp(dest, offset):
    _userp_fws.add((dest, offset))


class UserPBuffer(c.EUDObject):
    def __init__(self):
        super().__init__()

    def GetDataSize(self):  # noqa: N802
        return (len(_userp_fws) + 1) * 4

    def WritePayload(self, pbuf):  # noqa: N802
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
