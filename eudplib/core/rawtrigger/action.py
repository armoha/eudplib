#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TYPE_CHECKING

from typing_extensions import Self

from eudplib import utils as ut
from eudplib.localize import _

from ..allocator import ConstExpr, IsConstExpr
from .consttype import Byte, Dword, Word

if TYPE_CHECKING:
    from ..allocator.payload import ObjCollector, RlocInt_C, _PayloadBuffer
    from .rawtriggerdef import RawTrigger

_acttypes: dict[int, str] = {
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

    """Action class.

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

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(
        self,
        locid1: Dword,
        strid: Dword,
        wavid: Dword,
        time: Dword,
        player1: Dword,
        player2: Dword,
        unitid: Word,
        acttype: Byte,
        amount: Byte,
        flags: Byte,
        *,
        eudx: Word = 0,
    ) -> None:
        """See :mod:`eudplib.base.stocktrg` for stock actions list."""
        super().__init__()
        self.fields: list[Dword] = [
            locid1,
            strid,
            wavid,
            time,
            player1,
            player2,
            unitid,
            acttype,
            amount,
            flags,
            0,
            eudx,
        ]
        self.parenttrg: "RawTrigger | None" = None
        self.actindex: int | None = None

    def __copy__(self) -> "Action":
        return self.__class__(*self.fields[:10], eudx=self.fields[11])  # type: ignore[arg-type]

    def disable(self) -> None:
        if isinstance(self.fields[9], ConstExpr):
            raise ut.EPError(_("Can't disable non-const Action flags"))
        self.fields[9] |= 2

    # -------

    def _invalid_action(self, i: int) -> str:
        acttype = self.fields[7]
        actname = _acttypes[acttype] if isinstance(acttype, int) else acttype
        return _("Invalid fields for action{} {}:").format(i, actname)

    def CheckArgs(self, i: int) -> None:  # noqa: N802
        if all(IsConstExpr(field) for field in self.fields[:6]) and all(
            isinstance(field, int) for field in self.fields[6:]
        ):
            return

        error = [self._invalid_action(i)]
        fieldname = [
            "location",
            "string",
            "wav_string",
            "time",
            "player",
            "amount",
            "unit_type",
            "action_type",
            "modifier",
            "flags",
            "padding",
            "maskflag",
        ]
        acttype = self.fields[7]
        if isinstance(acttype, int):
            if acttype == 45:  # SetDeaths
                fieldname[0] = "bitmask"
            elif acttype == 48:  # GiveUnits
                fieldname[4] = "giver"
                fieldname[5] = "taker"
            elif acttype == 38:  # MoveLocation
                fieldname[0] = "move_location"
                fieldname[5] = "dest_location"
            elif acttype in (39, 46):  # MoveUnit, Order
                fieldname[0] = "start_location"
                fieldname[5] = "dest_location"
            elif acttype == 11:  # CreateUnitwithProperties
                fieldname[5] = "unit_properties"
            elif acttype in (15, 16):  # RunAIScript(At)
                fieldname[5] = "aiscript"
            elif acttype == 13:  #  SetSwitch
                fieldname[5] = "switch_id"

            if acttype in (21, 27, 37):  # LeaderBoard (Score),  SetScore
                fieldname[6] = "score_type"
            elif acttype in (19, 26, 35):
                fieldname[6] = "resource_type"
            elif acttype == 57:
                fieldname[6] = "ally_status"

            if acttype in (23, 25, 39, 48, 49, 50, 51, 52, 53):
                fieldname[8] = "count"
            elif acttype in (32, 42, 43):
                fieldname[8] = "propstate"
            elif acttype == 13:
                fieldname[8] = "switch_action"
            elif acttype == 46:
                fieldname[8] = "unit_order"

        for i, field in enumerate(self.fields):
            if (i < 6 and not IsConstExpr(field)) or (
                i >= 6 and not isinstance(field, int)
            ):
                error.append(
                    "\t" + _("invalid {}: {}").format(fieldname[i], repr(field))
                )

        raise ut.EPError("\n".join(error))

    def SetParentTrigger(self, trg: "RawTrigger", index: int) -> None:  # noqa: N802
        ut.ep_assert(
            self.parenttrg is None,
            _("Actions cannot be shared by two triggers."),
        )

        ut.ep_assert(trg is not None, _("Trigger should not be null."))
        ut.ep_assert(0 <= index < 64, _("Triggers out of range"))

        self.parenttrg = trg
        self.actindex = index

    def Evaluate(self) -> "RlocInt_C":  # noqa: N802
        if self.parenttrg is None or self.actindex is None:
            # fmt: off
            err = _("Orphan action. This often happens when you try to do arithmetics with actions.")  # noqa: E501
            # fmt: on
            raise ut.EPError(err)
        return self.parenttrg.Evaluate() + 8 + 320 + 32 * self.actindex

    def CollectDependency(self, pbuffer: "ObjCollector") -> None:  # noqa: N802
        for field in self.fields[:6]:
            if not isinstance(field, int):
                pbuffer.WriteDword(field)  # type: ignore[arg-type]

    def WritePayload(self, pbuffer: "_PayloadBuffer") -> None:  # noqa: N802
        pbuffer.WritePack("IIIIIIHBBBBH", self.fields)  # type: ignore[arg-type]
