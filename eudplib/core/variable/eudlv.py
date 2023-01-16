#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ...utils import i2b4
from .. import rawtrigger as bt
from ..eudobj import Db
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
            self._mask = 1 << EUDLightBool._bit
            EUDLightBool._bit += 1
        else:
            lv = EUDLightVariable()
            EUDLightBool._lv = lv
            self._basev = lv
            self._mask = 1
            EUDLightBool._bit = 1
        self._memaddr = self._basev._memaddr

    def getValueAddr(self):
        return self._memaddr

    def Set(self):
        return bt.SetMemoryX(self.getValueAddr(), bt.SetTo, self._mask, self._mask)

    def Clear(self):
        return bt.SetMemoryX(self.getValueAddr(), bt.SetTo, 0, self._mask)

    def Toggle(self):
        return bt.SetMemoryX(self.getValueAddr(), bt.Add, self._mask, self._mask)

    def IsSet(self):
        return bt.MemoryX(self.getValueAddr(), bt.AtLeast, 1, self._mask)

    def IsCleared(self):
        return bt.MemoryX(self.getValueAddr(), bt.Exactly, 0, self._mask)
