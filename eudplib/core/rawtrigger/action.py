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

from eudplib import utils as ut
from eudplib.localize import _

from ..allocator import ConstExpr, IsConstExpr

_acttypes = {
    0: "(no action)",
    1: "Victory",
    2: "Defeat",
    3: "PreserveTrigger",
    4: "Wait",
    5: "PauseGame",
    6: "UnpauseGame",
    7: "Transmission",
    8: "PlayWAV",
    9: "DisplayText",
    10: "CenterView",
    11: "CreateUnitWithProperties",
    12: "SetMissionObjectives",
    13: "SetSwitch",
    14: "SetCountdownTimer",
    15: "RunAIScript",
    16: "RunAIScriptAt",
    17: "LeaderBoardControl",
    18: "LeaderBoardControlAt",
    19: "LeaderBoardResources",
    20: "LeaderBoardKills",
    21: "LeaderBoardScore",
    22: "KillUnit",
    23: "KillUnitAt",
    24: "RemoveUnit",
    25: "RemoveUnitAt",
    26: "SetResources",
    27: "SetScore",
    28: "MinimapPing",
    29: "TalkingPortrait",
    30: "MuteUnitSpeech",
    31: "UnMuteUnitSpeech",
    32: "LeaderboardComputerPlayers",
    33: "LeaderboardGoalControl",
    34: "LeaderboardGoalControlAt",
    35: "LeaderboardGoalResources",
    36: "LeaderboardGoalKills",
    37: "LeaderboardGoalScore",
    38: "MoveLocation",
    39: "MoveUnit",
    40: "LeaderboardGreed",
    41: "SetNextScenario",
    42: "SetDoodadState",
    43: "SetInvincibility",
    44: "CreateUnit",
    45: "SetDeaths",
    46: "Order",
    47: "Comment",
    48: "GiveUnits",
    49: "ModifyUnitHitPoints",
    50: "ModifyUnitEnergy",
    51: "ModifyUnitShields",
    52: "ModifyUnitResourceAmount",
    53: "ModifyUnitHangarCount",
    54: "PauseTimer",
    55: "UnpauseTimer",
    56: "Draw",
    57: "SetAllianceStatus",
}


class Action(ConstExpr):

    """
    Action class.

    Memory layout.

     ======  ============= ========  ==========
     Offset  Field Name    Position  EPD Player
     ======  ============= ========  ==========
       +00   locid1         dword0   EPD(act)+0
       +04   strid          dword1   EPD(act)+1
       +08   wavid          dword2   EPD(act)+2
       +0C   time           dword3   EPD(act)+3
       +10   player1        dword4   EPD(act)+4
       +14   player2        dword5   EPD(act)+5
       +18   unitid         dword6   EPD(act)+6
       +1A   acttype
       +1B   amount
       +1C   flags          dword7   EPD(act)+7
       +1D   internal[3
     ======  ============= ========  ==========
    """

    # fmt: off
    def __init__(self, locid1, strid, wavid, time, player1, player2,
                 unitid, acttype, amount, flags, *, eudx=0):
        """
        See :mod:`eudplib.base.stocktrg` for stock actions list.
        """
        super().__init__(self)

        if isinstance(eudx, str):
            eudx = ut.b2i2(ut.u2b(eudx))
        self.fields = [locid1, strid, wavid, time, player1,
                       player2, unitid, acttype, amount, flags, 0, eudx]
        # fmt: on
        self.parenttrg = None
        self.actindex = None

    def Disabled(self) -> None:
        self.fields[9] |= 2

    # -------

    def CheckArgs(self, i: int) -> None:
        for n, field in enumerate(self.fields[:10]):
            if field is None or IsConstExpr(field):
                continue

            params = ["locid", "strid", "wavid", "time", "player", "amount", "unitid", "acttype", "modifier", "flags"]
            acttype = self.fields[7]
            if isinstance(acttype, int):
                if acttype == 45:
                    params[0] = "bitmask"
                elif acttype == 48:
                    params[4] = "giver"
                    params[5] = "taker"
                elif acttype == 38:
                    params[0] = "moveloc"
                    params[5] = "destloc"
                elif acttype in (39, 46):
                    params[0] = "startloc"
                    params[5] = "destloc"
                elif acttype == 11:
                    params[5] = "unitprop"
                elif acttype in (15, 16):
                    params[5] = "aiscript"
                elif acttype == 13:
                    params[5] = "switchid"

                if acttype in (21, 27, 37):
                    params[6] = "scoretype"
                elif acttype in (19, 26, 35):
                    params[6] = "resourcetype"
                elif acttype == 57:
                    params[6] = "allystatus"

                if acttype in (23, 25, 39, 48, 49, 50, 51, 52, 53):
                    params[8] = "count"
                elif acttype in (32, 42, 43):
                    params[8] = "propstate"
                elif acttype == 13:
                    params[8] = "switchaction"
                elif acttype == 46:
                    params[8] = "unitorder"

            try:
                acttype = _acttypes.get(acttype, "(unknown)")
            except TypeError:  # unhashable type
                acttype = "(unknown)"
            raise ut.EPError(_('Invalid {} "{}" in action{} "{}"').format(params[n], field, i, acttype))

    def SetParentTrigger(self, trg, index) -> None:
        ut.ep_assert(
            self.parenttrg is None, _("Actions cannot be shared by two triggers.")
        )

        ut.ep_assert(trg is not None, _("Trigger should not be null."))
        ut.ep_assert(0 <= index < 64, _("Triggers out of range"))

        self.parenttrg = trg
        self.actindex = index

    def Evaluate(self):
        return self.parenttrg.Evaluate() + 8 + 320 + 32 * self.actindex

    def CollectDependency(self, pbuffer) -> None:
        wdw = pbuffer.WriteDword
        fld = self.fields
        wdw(fld[0])
        wdw(fld[1])
        wdw(fld[2])
        wdw(fld[3])
        wdw(fld[4])
        wdw(fld[5])

    def WritePayload(self, pbuffer) -> None:
        pbuffer.WritePack("IIIIIIHBBBBH", self.fields)
