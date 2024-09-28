# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.
from math import log2

from typing_extensions import Self

from .. import core as c
from .. import utils as ut
from ..core.inplacecw import iand, ilshift, ior, irshift, iset, isub, ixor
from ..ctrlstru import EUDElse, EUDEndIf, EUDIf, EUDNot
from ..localize import _
from ..memio import f_dwread_epd, f_dwwrite_epd
from ..utils import EPError

_eudarray_has_instance = False
_ptr_array = False


def _use_ptr_array():
    global _ptr_array
    if _eudarray_has_instance:
        raise ut.EPError(_("EUDArray is already instantiated"))
    _ptr_array = True


class EUDArrayData(c.EUDObject):
    """
    Structure for storing multiple values.
    """

    __slots__ = ("_datas", "_arrlen")

    dont_flatten = True

    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls)

    def __init__(self, arr) -> None:
        global _eudarray_has_instance
        _eudarray_has_instance = True
        super().__init__()

        if isinstance(arr, int):
            arrlen = arr
            self._datas = [0] * arrlen
            self._arrlen = arrlen

        else:
            if any(not c.IsConstExpr(item) for item in arr):
                err = [_("Invalid item(s) for {}:").format(self.__class__)]
                for i, item in enumerate(arr):
                    if not c.IsConstExpr(item):
                        err.append(f"\t#{i}: {item}")
                raise ut.EPError("\n".join(err))
            self._datas = arr
            self._arrlen = len(arr)

    def GetDataSize(self) -> int:  # noqa: N802
        return self._arrlen * 4

    def WritePayload(self, buf) -> None:  # noqa: N802
        for item in self._datas:
            buf.WriteDword(item)

    # --------

    def GetArraySize(self) -> int:  # noqa: N802
        """Get size of array"""
        return self._arrlen


@c.EUDFunc
def _get_epd(ptr):
    if EUDIf()(ptr >= 1 << 31):
        ptr -= 1 << 31
    if EUDElse()():
        ut.EPD(ptr, ret=[ptr])
    EUDEndIf()
    c.EUDReturn(ptr)


class EUDArray(ut.ExprProxy):
    __slots__ = ("length", "_epd")
    dont_flatten = True

    def __init__(self, initval=None, *, _from=None) -> None:
        global _eudarray_has_instance
        _eudarray_has_instance = True
        self.length: int | None
        if _from is not None:
            data_obj = _from
            try:
                self.length = _from._arrlen
            except AttributeError:
                try:
                    self.length = _from.length
                except AttributeError:
                    self.length = None
            if _ptr_array:
                try:
                    self._epd = _from._epd
                except AttributeError:
                    if c.IsEUDVariable(_from):
                        self._epd = c.Forward()
                        c.SetNextTrigger(self._epd)
                        self._epd << c.NextTrigger()
                    else:
                        self._epd = ut.EPD(_from)

        else:
            data_obj = EUDArrayData(initval)
            self.length = data_obj._arrlen
            if not _ptr_array:
                data_obj = ut.EPD(data_obj)
            if _ptr_array:
                self._epd = ut.EPD(data_obj)
        if not _ptr_array:
            self._epd = data_obj

        super().__init__(data_obj)

    def Assign(self, other) -> Self:  # noqa: N802
        if not isinstance(self._value, c.EUDVariable):
            raise EPError(_("Can't assign {} to constant expression").format(other))
        if isinstance(other, type(self)):
            if _ptr_array:
                self._lazy_init_epd()
                other._lazy_init_epd()
                c.SetVariables([self._value, self._epd], [other, other._epd])
            else:
                c.SetVariables(self._value, other._value)
        elif isinstance(other, int) and other == 0:
            if _ptr_array:
                self._lazy_init_epd()
                c.SetVariables([self._value, self._epd], [0, 0])
            else:
                c.SetVariables(self._value, 0)
        elif isinstance(other, c.ConstExpr):
            if _ptr_array and other._is_aligned_ptr():
                c.SetVariables([self._value, self._epd], [other, ut.EPD(other)])
            elif not _ptr_array and other._is_epd():
                c.SetVariables(self._value, other)
        else:
            raise EPError(_("Can't assign {} to {}").format(other, self))
        return self

    def _lazy_init_epd(self) -> None:
        # lazy calculate self._epd
        if _ptr_array and type(self._epd) is c.Forward:
            if c.PushTriggerScope():
                nptr = self._epd.expr
                self._epd.Reset()
                self._epd << c.NextTrigger()
                self._epd = _get_epd(self)
                c.SetNextTrigger(nptr)
            c.PopTriggerScope()

    def _bound_check(self, index: object) -> None:
        index = ut.unProxy(index)
        if isinstance(index, int) and self.length is not None:
            ut.ep_assert(
                0 <= index < self.length,
                _("index out of bounds")
                + ": "
                + _("EUDArray.length is {} but the index is {}").format(
                    self.length, index
                ),
            )
        self._lazy_init_epd()

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
    # Total 6 cases = 3 x 2
    # 3 = [0, 1, 2] of (self._epd, key) are variable
    # 2 = val is variable or not
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
        self._bound_check(key)
        return EUDNot(c.MemoryEPD(self._epd + key, c.Exactly, val))

    def leitem(self, key, val):
        self._bound_check(key)
        return c.MemoryEPD(self._epd + key, c.AtMost, val)

    def geitem(self, key, val):
        self._bound_check(key)
        return c.MemoryEPD(self._epd + key, c.AtLeast, val)

    def ltitem(self, key, val):
        self._bound_check(key)
        return EUDNot(c.MemoryEPD(self._epd + key, c.AtLeast, val))

    def gtitem(self, key, val):
        self._bound_check(key)
        return EUDNot(c.MemoryEPD(self._epd + key, c.AtMost, val))
