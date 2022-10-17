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

from ..allocator import ConstExpr, IsConstExpr
from eudplib import utils as ut
from eudplib.localize import _
from inspect import getframeinfo, stack

_condtypes = {
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

    """
    Condition class.

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

    # fmt: off
    def __init__(self, locid, player, amount, unitid,
                 comparison, condtype, restype, flags, *, eudx=0):
        # self.decl = list()
        # for i in range(1, 9):
        #     try:
        #         decl = getframeinfo(stack()[i][0])
        #     except IndexError:
        #         break
        #     if decl.filename.startswith("E:\\eudplib\\eudplib\\"):
        #         continue
        #     self.decl.append(decl)
        super().__init__(self)

        if isinstance(eudx, str):
            eudx = ut.b2i2(ut.u2b(eudx))
        self.fields = [locid, player, amount, unitid,
                       comparison, condtype, restype, flags, eudx]
        # fmt: on
        self.parenttrg = None
        self.condindex = None

    def Disabled(self):
        self.fields[7] |= 2

    # -------

    def CheckArgs(self, i):
        for n, field in enumerate(self.fields[:8]):
            if field is None or IsConstExpr(field):
                continue

            params = ["locid", "player", "amount", "unitid", "comparison", "condtype", "resource","flags"]
            condtype = self.fields[5]
            if isinstance(condtype, int):
                if condtype == 15:
                    params[0] = "bitmask"
                elif condtype == 11:
                    params[4] = "switchstate"
                    params[6] = "switchid"
                if condtype in (9, 19, 21):
                    params[6] = "scoretype"

            try:
                condtype = _condtypes.get(condtype, "(unknown)")
            except TypeError:  # unhashable type
                condtype = "(unknown)"
            raise ut.EPError(_('Invalid {} "{}" in condition{} "{}"').format(params[n], field, i, condtype))

        return True

    def SetParentTrigger(self, trg, index):
        ut.ep_assert(
            self.parenttrg is None, _("Condition cannot be shared by two triggers.")
        )

        ut.ep_assert(trg is not None, _("Trigger should not be null."))
        ut.ep_assert(0 <= index < 16, _("Condition index should be 0 to 15"))

        self.parenttrg = trg
        self.condindex = index

    def Evaluate(self):
        if self.parenttrg is None:
            msg = []
            msg.append(_("Orphan condition. This often happens when you try to do arithmetics with conditions."))
            # msg.append(_("stack backtrace:"))
            # for decl in reversed(self.decl):
            #     errs = decl.filename, decl.lineno, decl.function
            #     msg.append("\t" + _("File {} Line {} in {}").format(*errs))
            raise ut.EPError("\n".join(msg))
        return self.parenttrg.Evaluate() + 8 + self.condindex * 20

    def CollectDependency(self, pbuffer):
        wdw = pbuffer.WriteDword
        fld = self.fields
        wdw(fld[0])
        wdw(fld[1])
        wdw(fld[2])

    def WritePayload(self, pbuffer):
        pbuffer.WritePack("IIIHBBBBH", self.fields)

    def __bool__(self):
        raise RuntimeError(_("To prevent error, Condition can't be put into if."))

    def Negate(self):
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
            self.fields[4] ^= 1
        elif condtype in comparison_set:
            bring_or_command = (2, 3)
            comparison = self.fields[4]
            amount = self.fields[2]
            ut.ep_assert(isinstance(comparison, int) and isinstance(amount, int))
            amount &= 0xFFFFFFFF
            if comparison == 10 and amount == 0:
                self.fields[4] = 0
                self.fields[2] = 1
            elif comparison == 0 and amount == 1:
                self.fields[4] = 10
                self.fields[2] = 0
            elif comparison == 0 and amount == 0:
                self.fields[5] = 23
            elif condtype in bring_or_command:
                # AtMost and Exactly/AtLeast behaves differently in Bring or Command.
                # (ex. AtMost counts buildings on construction and does not count Egg/Cocoon)
                # So only exchanging (Exactly, 0) <-> (AtLeast, 1) is sound.
                #
                # See: https://cafe.naver.com/edac/book5095361/96809
                raise ut.EPError(_("Bring and Command can't exchange AtMost and Exactly/AtLeast"))
            elif comparison in (0, 1):
                self.fields[4] ^= 1
                self.fields[2] += -((-1) ** comparison)
            elif comparison != 10:
                raise ut.EPError(_('Invalid comparison "{}" in trigger index {}').format(comparison, 0))
            elif condtype == 15 and self.fields[8] == ut.b2i2(ut.u2b("SC")):
                mask = self.fields[0] & 0xFFFFFFFF
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
