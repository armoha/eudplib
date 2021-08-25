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

from .. import rawtrigger as bt
from ..eudobj import Db
from ...utils import i2b4
from .vbase import VariableBase


class EUDLightVariable(VariableBase):
    def __init__(self, initvalue=0):
        super().__init__()
        self._memaddr = Db(i2b4(initvalue))

    def getValueAddr(self):
        return self._memaddr

    def checkNonRValue(self):
        pass

    def __hash__(self):
        return id(self)


class EUDLightBool:
    _lv = EUDLightVariable()
    _bit = 0

    def __init__(self):
        if EUDLightBool._bit < 32:
            self._basev = EUDLightBool._lv
            self._value = 1 << EUDLightBool._bit
            EUDLightBool._bit += 1
        else:
            lv = EUDLightVariable()
            EUDLightBool._lv = lv
            self._basev = lv
            self._value = 1
            EUDLightBool._bit = 1
        self._memaddr = self._basev._memaddr

    def getValueAddr(self):
        return self._memaddr

    def Set(self):
        return bt.SetMemoryX(self.getValueAddr(), bt.SetTo, self._value, self._value)

    def Clear(self):
        return bt.SetMemoryX(self.getValueAddr(), bt.SetTo, 0, self._value)

    def Toggle(self):
        return bt.SetMemoryX(self.getValueAddr(), bt.Add, self._value, self._value)

    def IsSet(self):
        return bt.MemoryX(self.getValueAddr(), bt.AtLeast, 1, self._value)

    def IsCleared(self):
        return bt.MemoryX(self.getValueAddr(), bt.Exactly, 0, self._value)
