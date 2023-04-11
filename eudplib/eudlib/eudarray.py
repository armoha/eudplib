#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.
from math import log2

from .. import core as c
from .. import utils as ut
from ..core.inplacecw import cpset, iand, ilshift, ior, irshift, iset, isub, ixor
from ..localize import _
from .memiof import f_dwadd_epd, f_dwread_epd, f_dwwrite_epd, f_setcurpl2cpcache


class EUDArrayData(c.EUDObject):
    """
    Structure for storing multiple values.
    """

    dontFlatten = True

    def __init__(self, arr) -> None:
        super().__init__()

        if isinstance(arr, int):
            arrlen = arr
            self._datas = [0] * arrlen
            self._arrlen = arrlen

        else:
            for i, item in enumerate(arr):
                ut.ep_assert(c.IsConstExpr(item), _("Invalid item #{}").format(i))
            self._datas = arr
            self._arrlen = len(arr)

    def GetDataSize(self) -> int:
        return self._arrlen * 4

    def WritePayload(self, buf) -> None:
        for item in self._datas:
            buf.WriteDword(item)

    # --------

    def GetArraySize(self) -> int:
        """Get size of array"""
        return self._arrlen


class EUDArray(ut.ExprProxy):
    dontFlatten = True

    def __init__(self, initval=None, *, _from=None) -> None:
        self.length: int | None
        if _from is not None:
            dataObj = _from
            try:
                self.length = _from._arrlen
            except AttributeError:
                self.length = None

        else:
            dataObj = EUDArrayData(initval)
            self.length = dataObj._arrlen

        super().__init__(dataObj)
        self._epd = ut.EPD(self)

    def fmt(self, formatter):
        if isinstance(self.length, int):
            formatter.write_str("[")
            for i in range(self.length):
                formatter.write_fmt("{}" if i == 0 else ", {}", self[i])
            formatter.write_str("]")
        else:
            formatter.write_fmt("[ptr=0x{:X}]", self)

    def _bound_check(self, index: object) -> None:
        index = ut.unProxy(index)
        if isinstance(index, int) and isinstance(self.length, int):
            ut.ep_assert(
                0 <= index < self.length,
                _("index out of bounds: EUDArray.length is {} but the index is {}").format(
                    self.length, index
                ),
            )

    def get(self, key) -> c.EUDVariable:
        self._bound_check(key)
        return f_dwread_epd(self._epd + key)

    def __getitem__(self, key) -> c.EUDVariable:
        return self.get(key)

    def set(self, key, item):
        self._bound_check(key)
        return iset(self._epd, key, c.SetTo, item)

    def __setitem__(self, key, item):
        return self.set(key, item)

    def __iter__(self):
        raise ut.EPError(_("Can't iterate EUDArray"))

    # in-place item operations
    # Total 6 cases = 3 × 2
    # [0, 1, 2] of (self._epd, key) are variable
    #  × val is variable or not
    def iadditem(self, key, val):
        self._bound_check(key)
        return iset(self._epd, key, c.Add, val)

    # FIXME: add operator for f_dwsubtract_epd
    def isubtractitem(self, key, val):
        self._bound_check(key)
        return iset(self._epd, key, c.Subtract, val)

    def isubitem(self, key, val):
        self._bound_check(key)
        return isub(self._epd, key, val)

    # defined when val is power of 2
    def imulitem(self, key, val):
        self._bound_check(key)
        if not isinstance(val, int):
            raise AttributeError
        if val == 0:
            return f_dwwrite_epd(self._epd + key, 0)
        # val is power of 2
        if val & (val - 1) == 0:
            return self.ilshiftitem(key, int(log2(val)))
        # val is negation of power of 2
        if -val & (-val - 1) == 0:
            pass
        raise AttributeError

    # defined when val is power of 2
    def ifloordivitem(self, key, val):
        self._bound_check(key)
        if not isinstance(val, int):
            raise AttributeError
        if val == 0:
            raise ZeroDivisionError
        # val is power of 2
        if val & (val - 1) == 0:
            return self.irshiftitem(key, int(log2(val)))
        # val is negation of power of 2
        if -val & (-val - 1) == 0:
            pass
        raise AttributeError

    # defined when val is power of 2
    def imoditem(self, key, val):
        self._bound_check(key)
        if not isinstance(val, int):
            raise AttributeError
        if val == 0:
            raise ZeroDivisionError
        # val is power of 2
        if val & (val - 1) == 0:
            return self.ianditem(key, val - 1)
        raise AttributeError

    # FIXME: merge logic with EUDVariable and VariableBase

    def ilshiftitem(self, key, val):
        self._bound_check(key)
        if isinstance(val, int):
            return ilshift(self._epd, key, val)
        raise AttributeError

    def irshiftitem(self, key, val):
        self._bound_check(key)
        if isinstance(val, int):
            return irshift(self._epd, key, val)
        raise AttributeError

    def ipowitem(self, key, val):
        self._bound_check(key)
        if isinstance(val, int) and val == 1:
            return
        raise AttributeError

    def ianditem(self, key, val):
        self._bound_check(key)
        iand(self._epd, key, val)

    def ioritem(self, key, val):
        self._bound_check(key)
        ior(self._epd, key, val)

    def ixoritem(self, key, val):
        self._bound_check(key)
        ixor(self._epd, key, val)

    # FIXME: Add operator?
    def iinvertitem(self, key):
        self._bound_check(key)
        return self.ixoritem(key, 0xFFFFFFFF)

    def inotitem(self, key):
        self._bound_check(key)
        raise AttributeError

    # item comparisons
    def eqitem(self, key, val):
        self._bound_check(key)
        return c.MemoryEPD(self._epd + key, c.Exactly, val)

    def neitem(self, key, val):
        from .utilf import EUDNot

        self._bound_check(key)
        return EUDNot(c.MemoryEPD(self._epd + key, c.Exactly, val))

    def leitem(self, key, val):
        self._bound_check(key)
        return c.MemoryEPD(self._epd + key, c.AtMost, val)

    def geitem(self, key, val):
        self._bound_check(key)
        return c.MemoryEPD(self._epd + key, c.AtLeast, val)

    def ltitem(self, key, val):
        from .utilf import EUDNot

        self._bound_check(key)
        return EUDNot(c.MemoryEPD(self._epd + key, c.AtLeast, val))

    def gtitem(self, key, val):
        from .utilf import EUDNot

        self._bound_check(key)
        return EUDNot(c.MemoryEPD(self._epd + key, c.AtMost, val))
