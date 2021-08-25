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
        ut.ep_assert(
            self.fields[0] is None or IsConstExpr(self.fields[0]),
            _('Invalid locid "{}" in trigger index {}').format(self.fields[0], i),
        )
        ut.ep_assert(
            self.fields[1] is None or IsConstExpr(self.fields[1]),
            _('Invalid player "{}" in trigger index {}').format(self.fields[1], i),
        )
        ut.ep_assert(
            self.fields[2] is None or IsConstExpr(self.fields[2]),
            _('Invalid amount "{}" in trigger index {}').format(self.fields[2], i),
        )
        ut.ep_assert(
            self.fields[3] is None or IsConstExpr(self.fields[3]),
            _('Invalid unitid "{}" in trigger index {}').format(self.fields[3], i),
        )
        ut.ep_assert(
            self.fields[4] is None or IsConstExpr(self.fields[4]),
            _('Invalid comparison "{}" in trigger index {}').format(self.fields[4], i),
        )
        ut.ep_assert(
            self.fields[5] is None or IsConstExpr(self.fields[5]),
            _('Invalid condtype "{}" in trigger index {}').format(self.fields[5], i),
        )
        ut.ep_assert(
            self.fields[6] is None or IsConstExpr(self.fields[6]),
            _('Invalid restype "{}" in trigger index {}').format(self.fields[6], i),
        )
        ut.ep_assert(
            self.fields[7] is None or IsConstExpr(self.fields[7]),
            _('Invalid flags "{}" in trigger index {}').format(self.fields[7], i),
        )
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
        ut.ep_assert(
            self.parenttrg is not None,
            _("Orphan condition. This often happens when you try to do arithmetics with conditions.")
        )
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
            amount = self.fields[2] & 0xFFFFFFFF
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
