#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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

from .. import rawtrigger as bt
from ...utils import EPD
from .eudv import EUDVariable, VariableTriggerForward


class EUDXVariable(EUDVariable):
    def __init__(self, initval=0, mask=~0):
        self._vartrigger = VariableTriggerForward(initval, mask)
        self._varact = self._vartrigger + (8 + 320)
        self._rvalue = False

    def getMaskAddr(self):
        return self._varact

    # -------

    def SetMask(self, value):
        return bt.SetMemory(self.getMaskAddr(), bt.SetTo, value)

    def AddMask(self, value):
        return bt.SetMemory(self.getMaskAddr(), bt.Add, value)

    def SubtractMask(self, value):
        return bt.SetMemory(self.getMaskAddr(), bt.Subtract, value)

    # -------

    def SetMaskX(self, value, mask):
        return bt.SetMemoryX(self.getMaskAddr(), bt.SetTo, value, mask)

    def AddMaskX(self, value, mask):
        return bt.SetMemoryX(self.getMaskAddr(), bt.Add, value, mask)

    def SubtractMaskX(self, value, mask):
        return bt.SetMemoryX(self.getMaskAddr(), bt.Subtract, value, mask)

    # -------

    def MaskAtLeast(self, value):
        return bt.Memory(self.getMaskAddr(), bt.AtLeast, value)

    def MaskAtMost(self, value):
        return bt.Memory(self.getMaskAddr(), bt.AtMost, value)

    def MaskExactly(self, value):
        return bt.Memory(self.getMaskAddr(), bt.Exactly, value)

    # -------

    def MaskAtLeastX(self, value, mask):
        return bt.MemoryX(self.getMaskAddr(), bt.AtLeast, value, mask)

    def MaskAtMostX(self, value, mask):
        return bt.MemoryX(self.getMaskAddr(), bt.AtMost, value, mask)

    def MaskExactlyX(self, value, mask):
        return bt.MemoryX(self.getMaskAddr(), bt.Exactly, value, mask)
