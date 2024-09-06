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

from ...core.eudfunc.eudf import _EUDPredefineReturn
from ...localize import _
from ...memio import f_getcurpl, f_setcurpl
from ...offsetmap.scdata import Force1, Force2, Force3, Force4, TrgPlayer


@_EUDPredefineReturn(2, 3)
@c.EUDTypedFunc([TrgPlayer], [None])
def f_playerexist(player):
    """Check if player has not left the game.

    :returns: 1 if player exists, 0 if not.
    """
    ret = f_playerexist._frets[0]
    pts = 0x51A280

    cs.EUDSwitch(player)
    block = ut.EUDGetLastBlockOfName("swblock")[1]
    block["_actions"].append(ret.SetNumber(1))
    for p in ut._rand_lst(range(8)):
        if cs.EUDSwitchCase()(p):
            c.RawTrigger(
                nextptr=block["swend"],
                conditions=c.Memory(
                    pts + p * 12 + 8, c.Exactly, ~(pts + p * 12 + 4)
                ),
                actions=ret.SetNumber(0),
            )

    if cs.EUDSwitchDefault()():
        ret << 0
    cs.EUDEndSwitch()
    # return ret


# --------


def EUDLoopPlayer(  # noqa: N802
    ptype: str | None = "Human", force=None, race: str | None = None
) -> Iterator[TrgPlayer]:
    def encode_force(f):
        force_dict = {Force1: 0, Force2: 1, Force3: 2, Force4: 3}
        if not isinstance(f, int) and f in force_dict:
            return force_dict[f]
        return f

    plist = []
    for p in range(8):
        pinfo = c.GetPlayerInfo(p)
        if (
            (not ptype or pinfo.typestr == ptype)
            and (not force or pinfo.force == encode_force(force))
            and (not race or pinfo.racestr == race)
        ):
            plist.append(p)
    ut.EUDCreateBlock("loopplayerblock", None)
    if not plist:
        e = []
        e.append(_("No player met condition for input map settings:"))
        if ptype:
            e.append(_(" type {}").format(ptype))
        if force:
            e.append(_(" force {}").format(force))
        if race:
            e.append(_(" race {}").format(race))
        e.append("\n")
        e.append(_("Check out whether Start Locations are placed correctly."))
        raise ut.EPError("".join(e))
    start, end = min(plist), max(plist)

    v = c.EUDVariable()
    v << start
    if cs.EUDWhile()(v <= end):
        for i in range(start, end):
            if i not in plist:
                cs.EUDContinueIf(v == i)
        cs.EUDContinueIfNot(f_playerexist(v))
        yield TrgPlayer.cast(v)
        cs.EUDSetContinuePoint()
        v += 1
    cs.EUDEndWhile()
    ut.EUDPopBlock("loopplayerblock")


# -------


def EUDPlayerLoop():  # noqa: N802
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


def EUDEndPlayerLoop():  # noqa: N802
    block = ut.EUDPopBlock("ploopblock")[1]
    playerv = block["playerv"]
    origcp = block["origcp"]

    if not cs.EUDIsContinuePointSet():
        cs.EUDSetContinuePoint()

    playerv += 1
    cs.EUDEndWhile()
    f_setcurpl(origcp)
