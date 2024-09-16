# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from typing_extensions import Self

from ... import utils as ut
from ...localize import _
from ..allocator import ConstExpr, IsConstExpr
from .consttype import Byte, Dword, Word

if TYPE_CHECKING:
    from ..allocator.payload import ObjCollector, RlocInt_C, _PayloadBuffer
    from .rawtriggerdef import RawTrigger

_condtypes: dict[int, str] = {
    0: "(no condition)",
    1: "CountdownTimer",
    2: "Command",
    3: "Bring",
    4: "Accumulate",
    5: "Kills",
    6: "CommandMost",
    7: "CommandMostAt",
    8: "MostKills",
    9: "HighestScore",
    10: "MostResources",
    11: "Switch",
    12: "ElapsedTime",
    14: "Opponents",
    15: "Deaths",
    16: "CommandLeast",
    17: "CommandLeastAt",
    18: "LeastKills",
    19: "LowestScore",
    20: "LeastResources",
    21: "Score",
    22: "Always",
    23: "Never",
}


class Condition(ConstExpr):
    """Condition class.

    Memory layout:

     ======  =============  ========  ===========
     Offset  Field name     Position  EPD Player
     ======  =============  ========  ===========
       +00   locid           dword0   EPD(cond)+0
       +04   player          dword1   EPD(cond)+1
       +08   amount          dword2   EPD(cond)+2
       +0C   unitid          dword3   EPD(cond)+3
       +0E   comparison
       +0F   condtype
       +10   restype         dword4   EPD(cond)+4
       +11   flags
       +12   internal[2]
     ======  =============  ========  ===========
    """

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(
        self,
        locid: Dword,
        player: Dword,
        amount: Dword,
        unitid: Word,
        comparison: Byte,
        condtype: Byte,
        restype: Byte,
        flags: Byte,
        *,
        eudx: Word = 0,
    ) -> None:
        """See :mod:`eudplib.base.stockcond` for stock conditions list."""
        super().__init__()
        self.fields: list[Dword] = [
            locid,
            player,
            amount,
            unitid,
            comparison,
            condtype,
            restype,
            flags,
            eudx,
        ]
        self.parenttrg: RawTrigger | None = None
        self.condindex: int | None = None

    def __copy__(self) -> Condition:
        return self.__class__(*self.fields[:8], eudx=self.fields[8])  # type: ignore[arg-type]

    def disable(self) -> None:
        if isinstance(self.fields[7], ConstExpr):
            raise ut.EPError(_("Can't disable non-const Condition flags"))
        self.fields[7] |= 2

    # -------

    def _invalid_condition(self, i: int) -> str:
        condtype = self.fields[5]
        condname = _condtypes[condtype] if isinstance(condtype, int) else condtype
        return _("Invalid fields for condition{} {}:").format(i, condname)

    def CheckArgs(self, i: int) -> None:  # noqa: N802
        fields = self.fields

        if (
            IsConstExpr(fields[0])
            and IsConstExpr(fields[1])
            and IsConstExpr(fields[2])
            and isinstance(fields[3], int)
            and isinstance(fields[4], int)
            and isinstance(fields[5], int)
            and isinstance(fields[6], int)
            and isinstance(fields[7], int)
            and isinstance(fields[8], int)
        ):
            return

        error = [self._invalid_condition(i)]
        fieldname = [
            "location",
            "player",
            "amount",
            "unit_type",
            "comparison",
            "condition_type",
            "resource_type",
            "flags",
            "maskflag",
        ]
        condtype = fields[5]
        if isinstance(condtype, int):
            if condtype == 15:
                fieldname[0] = "bitmask"
            elif condtype == 11:
                fieldname[4] = "switchstate"
                fieldname[6] = "switchid"
            if condtype in (9, 19, 21):
                fieldname[6] = "scoretype"

        for i, field in enumerate(fields):
            if (i < 3 and not IsConstExpr(field)) or (
                i >= 3 and not isinstance(field, int)
            ):
                error.append(
                    "\t" + _("invalid {}: {}").format(fieldname[i], repr(field))
                )

        raise ut.EPError("\n".join(error))

    def SetParentTrigger(self, trg: RawTrigger, index: int) -> None:  # noqa: N802
        if self.parenttrg is not None:
            raise ut.EPError(_("Condition cannot be shared by two triggers."))
        if trg is None:
            raise ut.EPError(_("Trigger should not be null."))
        if not (0 <= index < 16):
            raise ut.EPError(_("Condition index should be 0 to 15"))

        self.parenttrg = trg
        self.condindex = index

    def Evaluate(self) -> RlocInt_C:  # noqa: N802
        if self.parenttrg is None or self.condindex is None:
            # fmt: off
            raise ut.EPError(_("Orphan condition. This often happens when you try to do arithmetics with conditions."))  # noqa: E501
            # fmt: on
        return self.parenttrg.Evaluate() + 8 + self.condindex * 20

    def CollectDependency(self, pbuffer: ObjCollector) -> None:  # noqa: N802
        for field in self.fields[:3]:
            pbuffer.WriteDword(field)  # type: ignore[arg-type]

    def WritePayload(self, pbuffer: _PayloadBuffer) -> None:  # noqa: N802
        pbuffer.WritePack("IIIHBBBBH", self.fields)  # type: ignore[arg-type]

    def __bool__(self) -> NoReturn:
        raise RuntimeError(_("To prevent error, Condition can't be put into if."))

    def negate(self) -> None:
        condtype = self.fields[5]
        ut.ep_assert(isinstance(condtype, int))
        comparison_set = (1, 2, 3, 4, 5, 12, 14, 15, 21)
        always_set = (0, 22)
        never_set = (13, 23)
        if condtype in always_set:
            self.fields[5] = 23
        elif condtype in never_set:
            self.fields[5] = 22
        elif condtype == 11:  # Switch
            self.fields[4] ^= 1  # type: ignore[operator]
        elif condtype in comparison_set:
            bring_or_command = (2, 3)
            comparison = self.fields[4]
            amount = self.fields[2]
            ut.ep_assert(isinstance(comparison, int) and isinstance(amount, int))
            amount &= 0xFFFFFFFF  # type: ignore[operator]
            if comparison == 10 and amount == 0:
                self.fields[4] = 0
                self.fields[2] = 1
            elif comparison == 0 and amount == 1:
                self.fields[4] = 10
                self.fields[2] = 0
            elif comparison == 0 and amount == 0:
                self.fields[5] = 23
            # AtMost and Exactly/AtLeast behaves differently in Bring/Command
            # (AtMost counts buildings on construction and does not count Egg)
            # So only exchanging (Exactly, 0) <-> (AtLeast, 1) is sound.
            #
            # See: https://cafe.naver.com/edac/book5095361/96809
            elif condtype in bring_or_command:
                # fmt: off
                raise ut.EPError(_("Bring and Command can't exchange AtMost and Exactly/AtLeast"))  # noqa: E501
                # fmt: on
            elif comparison in (0, 1):
                self.fields[4] ^= 1  # type: ignore[operator]
                self.fields[2] += -((-1) ** comparison)  # type: ignore[operator]
            elif comparison != 10:
                raise ut.EPError(
                    _('Invalid comparison "{}" in trigger index {}').format(
                        comparison, 0
                    )
                )
            elif condtype == 15 and self.fields[8] == ut.b2i2(ut.u2b("SC")):
                mask = self.fields[0] & 0xFFFFFFFF  # type: ignore[operator]
                if amount & (~mask):  # never
                    self.fields[5] = 23
                elif amount == mask:
                    self.fields[4] = 1
                    self.fields[2] = mask - 1
                else:
                    raise ut.EPError(_("Can't negate EUDX condition"))
            elif amount == 0xFFFFFFFF:
                self.fields[4] = 1  # AtMost
                self.fields[2] = 0xFFFFFFFE
            else:
                raise ut.EPError(_("Can't negate condition with comparison"))
        else:
            raise ut.EPError(_("Can't negate condition"))
