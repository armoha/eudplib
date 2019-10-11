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
                 unitid, acttype, amount, flags, eudx=0):
        """
        See :mod:`eudplib.base.stocktrg` for stock actions list.
        """
        super().__init__(self)

        if eudx:
            eudx = ut.b2i2(b"SC")
        self.fields = [locid1, strid, wavid, time, player1,
                       player2, unitid, acttype, amount, flags, 0, eudx]
        # fmt: on
        self.parenttrg = None
        self.actindex = None
    def Disabled(self):
        self.fields[9] |= 2

    # -------

    def CheckArgs(self, i):
        ut.ep_assert(
            self.fields[0] is None or IsConstExpr(self.fields[0]),
            'Invalid locid1 "%s" in trigger index %d' % (self.fields[0], i),
        )
        ut.ep_assert(
            self.fields[1] is None or IsConstExpr(self.fields[1]),
            'Invalid strid "%s" in trigger index %d' % (self.fields[1], i),
        )
        ut.ep_assert(
            self.fields[2] is None or IsConstExpr(self.fields[2]),
            'Invalid wavid "%s" in trigger index %d' % (self.fields[2], i),
        )
        ut.ep_assert(
            self.fields[3] is None or IsConstExpr(self.fields[3]),
            'Invalid time "%s" in trigger index %d' % (self.fields[3], i),
        )
        ut.ep_assert(
            self.fields[4] is None or IsConstExpr(self.fields[4]),
            'Invalid player1 "%s" in trigger index %d' % (self.fields[4], i),
        )
        ut.ep_assert(
            self.fields[5] is None or IsConstExpr(self.fields[5]),
            'Invalid player2 "%s" in trigger index %d' % (self.fields[5], i),
        )
        ut.ep_assert(
            self.fields[6] is None or IsConstExpr(self.fields[6]),
            'Invalid unitid "%s" in trigger index %d' % (self.fields[6], i),
        )
        ut.ep_assert(
            self.fields[7] is None or IsConstExpr(self.fields[7]),
            'Invalid acttype "%s" in trigger index %d' % (self.fields[7], i),
        )
        ut.ep_assert(
            self.fields[8] is None or IsConstExpr(self.fields[8]),
            'Invalid amount "%s" in trigger index %d' % (self.fields[8], i),
        )
        ut.ep_assert(
            self.fields[9] is None or IsConstExpr(self.fields[9]),
            'Invalid flags "%s" in trigger index %d' % (self.fields[9], i),
        )
        return True

    def SetParentTrigger(self, trg, index):
        ut.ep_assert(
            self.parenttrg is None, "Actions cannot be shared by two triggers."
        )

        ut.ep_assert(trg is not None, "Trigger should not be null.")
        ut.ep_assert(0 <= index < 64, "Triggers out of range")

        self.parenttrg = trg
        self.actindex = index

    def Evaluate(self):
        return self.parenttrg.Evaluate() + 8 + 320 + 32 * self.actindex

    def CollectDependency(self, pbuffer):
        wdw = pbuffer.WriteDword
        fld = self.fields
        wdw(fld[0])
        wdw(fld[1])
        wdw(fld[2])
        wdw(fld[3])
        wdw(fld[4])
        wdw(fld[5])

    def WritePayload(self, pbuffer):
        pbuffer.WritePack("IIIIIIHBBBBH", self.fields)
