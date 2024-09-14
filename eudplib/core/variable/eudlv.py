# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ...utils import EPD, i2b4
from .. import rawtrigger as bt
from ..eudobj import Db
from .vbase import VariableBase


class EUDLightVariable(VariableBase):
    __slots__ = ("_memaddr",)

    def __init__(self, initvalue=0, /):
        super().__init__()
        self._memaddr = Db(i2b4(initvalue))

    def getValueAddr(self):  # noqa: N802
        return self._memaddr

    def checkNonRValue(self):  # noqa: N802
        pass

    def __hash__(self):
        return id(self)


class EUDLightBool:
    __slots__ = ("_mask", "_memaddr", "_memepd")
    _init_true_lv = EUDLightVariable(0xFFFFFFFF)
    _init_true_bit = 0
    _init_false_lv = EUDLightVariable(0)
    _init_false_bit = 0

    def __init__(self, initval: bool = False, /):
        if initval:
            if EUDLightBool._init_true_bit >= 32:
                EUDLightBool._init_true_lv = EUDLightVariable(0xFFFFFFFF)
                EUDLightBool._init_true_bit = 0
            lv = EUDLightBool._init_true_lv
            bit = EUDLightBool._init_true_bit
            EUDLightBool._init_true_bit += 1
        else:
            if EUDLightBool._init_false_bit >= 32:
                EUDLightBool._init_false_lv = EUDLightVariable(0)
                EUDLightBool._init_false_bit = 0
            lv = EUDLightBool._init_false_lv
            bit = EUDLightBool._init_false_bit
            EUDLightBool._init_false_bit += 1

        self._mask = 1 << bit
        self._memaddr = lv._memaddr
        self._memepd = EPD(lv._memaddr)

    def getValueAddr(self):  # noqa: N802
        return self._memaddr

    def Set(self):  # noqa: N802
        return bt.SetMemoryXEPD(self._memepd, bt.SetTo, self._mask, self._mask)

    def Clear(self):  # noqa: N802
        return bt.SetMemoryXEPD(self._memepd, bt.SetTo, 0, self._mask)

    def Toggle(self):  # noqa: N802
        return bt.SetMemoryXEPD(self._memepd, bt.Add, self._mask, self._mask)

    def IsSet(self):  # noqa: N802
        return bt.MemoryXEPD(self._memepd, bt.AtLeast, 1, self._mask)

    def IsCleared(self):  # noqa: N802
        return bt.MemoryXEPD(self._memepd, bt.Exactly, 0, self._mask)
