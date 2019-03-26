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
                 comparison, condtype, restype, flags, eudx=0):
        super().__init__(self)

        if eudx:
            eudx = ut.b2i2(b"SC")
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
            'Invalid locid "%s" in trigger index %d' % (self.fields[0], i),
        )
        ut.ep_assert(
            self.fields[1] is None or IsConstExpr(self.fields[1]),
            'Invalid player "%s" in trigger index %d' % (self.fields[1], i),
        )
        ut.ep_assert(
            self.fields[2] is None or IsConstExpr(self.fields[2]),
            'Invalid amount "%s" in trigger index %d' % (self.fields[2], i),
        )
        ut.ep_assert(
            self.fields[3] is None or IsConstExpr(self.fields[3]),
            'Invalid unitid "%s" in trigger index %d' % (self.fields[3], i),
        )
        ut.ep_assert(
            self.fields[4] is None or IsConstExpr(self.fields[4]),
            'Invalid comparison "%s" in trigger index %d' % (self.fields[4], i),
        )
        ut.ep_assert(
            self.fields[5] is None or IsConstExpr(self.fields[5]),
            'Invalid condtype "%s" in trigger index %d' % (self.fields[5], i),
        )
        ut.ep_assert(
            self.fields[6] is None or IsConstExpr(self.fields[6]),
            'Invalid restype "%s" in trigger index %d' % (self.fields[6], i),
        )
        ut.ep_assert(
            self.fields[7] is None or IsConstExpr(self.fields[7]),
            'Invalid flags "%s" in trigger index %d' % (self.fields[7], i),
        )
        return True

    def SetParentTrigger(self, trg, index):
        ut.ep_assert(
            self.parenttrg is None, "Condition cannot be shared by two triggers. "
        )

        ut.ep_assert(trg is not None, "Trigger should not be null.")
        ut.ep_assert(0 <= index < 16, "WTF")

        self.parenttrg = trg
        self.condindex = index

    def Evaluate(self):
        ut.ep_assert(
            self.parenttrg is not None,
            "Orphan condition. This often happens when you try to do "
            + "arithmetics with conditions.",
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
        raise RuntimeError("To prevent error, Condition can't be put into if.")
