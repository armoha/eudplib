#!/usr/bin/python
# -*- coding: utf-8 -*-
# cython: language_level=3

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

from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, overload

from ... import utils as ut
from ...localize import _
from ...utils import ExprProxy, unProxy
from .rlocint cimport RlocInt_C, toRlocInt


cdef class ConstExpr:
    """Class for general expression with rlocints."""

    cdef public unsigned int offset, rlocmode
    cdef public ConstExpr baseobj

    def __init__(
        self,
        baseobj: "ConstExpr | ExprProxy[ConstExpr | None] | None",
        offset: int = 0,
        rlocmode: int = 4,
    ) -> None:
        self.baseobj: "ConstExpr | None" = unProxy(baseobj)
        self.offset: int = offset & 0xFFFFFFFF
        self.rlocmode: int = rlocmode & 0xFFFFFFFF

    cpdef RlocInt_C Evaluate(self) -> RlocInt_C:
        if self.rlocmode:
            return self.baseobj.Evaluate() * self.rlocmode // 4 + self.offset  # type: ignore[union-attr]
        else:
            return RlocInt_C(self.offset & 0xFFFFFFFF, 0)

    # Cython version!

    def __add__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> "ConstExpr | int":
        other = ut.unProxy(other)
        if isinstance(other, int):
            return IntOrConstExpr(self.baseobj, self.offset + other, self.rlocmode)
        if isinstance(other, ConstExpr):
            if other.rlocmode == 0:
                return IntOrConstExpr(self.baseobj, self.offset + other.offset, self.rlocmode)
            if self.baseobj is other.baseobj:
                return IntOrConstExpr(
                    self.baseobj, self.offset + other.offset, self.rlocmode + other.rlocmode
                )
        return NotImplemented

    def __radd__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> "ConstExpr | int":
        return self.__add__(other)

    def __sub__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> "ConstExpr | int":
        other = ut.unProxy(other)
        if isinstance(other, int):
            return IntOrConstExpr(self.baseobj, self.offset - other, self.rlocmode)
        if isinstance(other, ConstExpr):
            if other.rlocmode == 0:
                return IntOrConstExpr(self.baseobj, self.offset - other.offset, self.rlocmode)
            if self.baseobj is other.baseobj:
                return IntOrConstExpr(
                    self.baseobj, self.offset - other.offset, self.rlocmode - other.rlocmode
                )
        return NotImplemented

    def __rsub__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> "ConstExpr | int":
        other = ut.unProxy(other)
        if isinstance(other, int):
            return IntOrConstExpr(self.baseobj, other - self.offset, -self.rlocmode)
        if isinstance(other, ConstExpr):
            if other.rlocmode == 0:
                return IntOrConstExpr(self.baseobj, other.offset - self.offset, -self.rlocmode)
            if self.baseobj is other.baseobj:
                return IntOrConstExpr(
                    self.baseobj, other.offset - self.offset, other.rlocmode - self.rlocmode
                )
        return NotImplemented

    def __mul__(self, other: "int | ExprProxy[int]") -> "ConstExpr | int":
        other = ut.unProxy(other)
        if isinstance(other, int):
            return IntOrConstExpr(self.baseobj, self.offset * other, self.rlocmode * other)
        return NotImplemented

    def __rmul__(self, other: "int | ExprProxy[int]") -> "ConstExpr | int":
        return self.__mul__(other)

    def __floordiv__(self, other: "int | ExprProxy[int]") -> "ConstExpr":
        other = ut.unProxy(other)
        if isinstance(other, int):
            ut.ep_assert(
                self.rlocmode % other == 0,
                _("Address not divisible; {} is not a factor of {}").format(other, self.rlocmode),
            )
            return ConstExpr(self.baseobj, self.offset // other, self.rlocmode // other)
        return NotImplemented

    def __mod__(self, other: "int | ExprProxy[int]") -> int:
        other = ut.unProxy(other)
        if isinstance(other, int):
            ut.ep_assert(
                self.rlocmode % other == 0,
                _("Address not divisible; {} is not a factor of {}").format(other, self.rlocmode),
            )
            return self.offset % other
        return NotImplemented

    def __neg__(self) -> "ConstExpr | int":
        return self.__mul__(-1)

    def __eq__(self, other) -> bool:
        other = ut.unProxy(other)
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset == other
        if isinstance(other, ConstExpr) and self.baseobj is other.baseobj:
            return (self.offset == other.offset) and (self.rlocmode == other.rlocmode)
        return NotImplemented

    def __hash__(self) -> int:
        return id(self)

    def __ne__(self, other) -> bool:
        other = ut.unProxy(other)
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset != other
        if isinstance(other, ConstExpr) and self.baseobj is other.baseobj:
            return (self.offset != other.offset) or (self.rlocmode != other.rlocmode)
        return NotImplemented

    def __lt__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> bool:
        other = ut.unProxy(other)
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset < other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset < other.offset
        return NotImplemented

    def __gt__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> bool:
        other = ut.unProxy(other)
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset > other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset > other.offset
        return NotImplemented

    def __le__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> bool:
        other = ut.unProxy(other)
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset <= other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset <= other.offset
        return NotImplemented

    def __ge__(self, other: "ConstExpr | int | ExprProxy[int | ConstExpr]") -> bool:
        other = ut.unProxy(other)
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset >= other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset >= other.offset
        return NotImplemented


def IntOrConstExpr(baseobj: ConstExpr | None, offset: int, rlocmode: int) -> int | ConstExpr:
    if rlocmode == 0:
        return offset
    return ConstExpr(baseobj, offset, rlocmode)


_ConstExpr = TypeVar("_ConstExpr", bound=ConstExpr)
_ConstExprProxy = TypeVar("_ConstExprProxy", bound=ExprProxy[ConstExpr])


cdef class Forward(ConstExpr):
    """Class for forward definition."""

    cdef public ConstExpr _expr

    def __init__(self) -> None:
        super().__init__(self)
        self._expr: ConstExpr | None = None
        self.dontFlatten = True

    @overload
    def __lshift__(self, expr: _ConstExpr) -> _ConstExpr:
        ...

    @overload
    def __lshift__(self, expr: _ConstExprProxy) -> _ConstExprProxy:
        ...

    @overload
    def __lshift__(self, expr: int) -> int:
        ...

    def __lshift__(self, expr):
        if self._expr is not None:
            raise ut.EPError(_("Reforwarding without reset is not allowed"))
        if expr is None:
            raise ut.EPError(_("Cannot forward to None"))
        unproxy = ut.unProxy(expr)
        if isinstance(unproxy, int):
            self._expr = ConstExpr(None, unproxy, 0)
        else:
            self._expr = unproxy
        return expr

    def IsSet(self) -> bool:
        return self._expr is not None

    def Reset(self) -> None:
        self._expr = None

    cpdef RlocInt_C Evaluate(self) -> RlocInt_C:
        if self._expr is None:
            raise ut.EPError(_("Forward not initialized"))
        return self._expr.Evaluate()

    def __call__(self, *args, **kwargs):
        if self._expr is None:
            raise ut.EPError(_("Forward not initialized"))
        return self._expr(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._expr, name)

    def __getitem__(self, name):
        if self._expr is None:
            raise ut.EPError(_("Forward not initialized"))
        return self._expr[name]

    def __setitem__(self, name, newvalue):
        if self._expr is None:
            raise ut.EPError(_("Forward not initialized"))
        self._expr[name] = newvalue


Evaluable: TypeAlias = ConstExpr | int | ExprProxy[ConstExpr] | RlocInt_C


cpdef RlocInt_C Evaluate(x: Evaluable) -> RlocInt_C:
    """Evaluate expressions"""
    expr = ut.unProxy(x)
    if isinstance(expr, ConstExpr):
        return expr.Evaluate()
    if isinstance(expr, (int, RlocInt_C)):
        return toRlocInt(expr)
    if x is expr:
        raise AttributeError(_("Only ConstExpr can be Evaluated, not {}").format(x))
    raise AttributeError(_("ExprProxy {} does not wrap ConstExpr, instead {}").format(x, expr))


def IsConstExpr(x) -> bool:
    return isinstance(ut.unProxy(x), (ConstExpr, int, RlocInt_C))
