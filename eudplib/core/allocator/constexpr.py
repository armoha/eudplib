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

from typing import TYPE_CHECKING, Any, TypeAlias, TypeVar, overload

from ... import utils as ut
from ...localize import _
from .rlocint import RlocInt_C, toRlocInt

if TYPE_CHECKING:
    from ...utils import ExprProxy


class ConstExpr:
    """Class for general expression with rlocints."""

    def __init__(
        self, baseobj: "ConstExpr | ExprProxy | None", offset: int = 0, rlocmode: int = 4
    ) -> None:
        self.baseobj: "ConstExpr | ExprProxy | None" = baseobj
        self.offset: int = offset & 0xFFFFFFFF
        self.rlocmode: int = rlocmode & 0xFFFFFFFF

    def Evaluate(self) -> RlocInt_C:
        if self.baseobj is None:
            raise ut.EPError(_("baseobj is None; Must override Evaluate"))
        return self.baseobj.Evaluate() * self.rlocmode // 4 + self.offset

    @overload
    def __add__(self, other: int) -> "ConstExpr":
        ...

    @overload
    def __add__(self, other: "ConstExpr | ExprProxy") -> "ConstExpr | int":
        ...

    def __add__(self, other):
        other = ut.unProxy(other)
        if isinstance(other, int):
            return ConstExpr(self.baseobj, self.offset + other, self.rlocmode)
        if _total_ord(self, other):
            if self.rlocmode + other.rlocmode == 0:
                return self.offset + other.offset
            return ConstExpr(
                self.baseobj, self.offset + other.offset, self.rlocmode + other.rlocmode
            )
        return NotImplemented

    @overload
    def __radd__(self, other: int) -> "ConstExpr":
        ...

    @overload
    def __radd__(self, other: "ConstExpr | ExprProxy") -> "ConstExpr | int":
        ...

    def __radd__(self, other):
        return self.__add__(other)

    @overload
    def __sub__(self, other: int) -> "ConstExpr":
        ...

    @overload
    def __sub__(self, other: "ConstExpr | ExprProxy") -> "ConstExpr | int":
        ...

    def __sub__(self, other):
        other = ut.unProxy(other)
        if isinstance(other, int):
            return ConstExpr(self.baseobj, self.offset - other, self.rlocmode)
        elif _total_ord(self, other):
            if self.rlocmode == other.rlocmode:
                return self.offset - other.offset
            return ConstExpr(
                self.baseobj, self.offset - other.offset, self.rlocmode - other.rlocmode
            )
        return NotImplemented

    @overload
    def __rsub__(self, other: int) -> "ConstExpr":
        ...

    @overload
    def __rsub__(self, other: "ConstExpr | ExprProxy") -> "ConstExpr | int":
        ...

    def __rsub__(self, other):
        other = ut.unProxy(other)
        if isinstance(other, int):
            return ConstExpr(self.baseobj, other - self.offset, -self.rlocmode)
        elif _total_ord(self, other):
            if self.rlocmode == other.rlocmode:
                return other.offset - self.offset
            return ConstExpr(
                self.baseobj, other.offset - self.offset, other.rlocmode - self.rlocmode
            )
        return NotImplemented

    def __mul__(self, other: "int | ExprProxy") -> "ConstExpr | int":
        other = ut.unProxy(other)
        if isinstance(other, int):
            if other == 0:
                return 0
            return ConstExpr(self.baseobj, self.offset * other, self.rlocmode * other)
        return NotImplemented

    def __rmul__(self, other: "int | ExprProxy") -> "ConstExpr | int":
        return self.__mul__(other)

    def __floordiv__(self, other: "int | ExprProxy") -> "ConstExpr":
        other = ut.unProxy(other)
        if isinstance(other, int):
            ut.ep_assert(
                self.rlocmode % other == 0,
                _("Address not divisible; {} is not a factor of {}").format(other, self.rlocmode),
            )
            return ConstExpr(self.baseobj, self.offset // other, self.rlocmode // other)
        return NotImplemented

    def __mod__(self, other: "int | ExprProxy") -> int:
        other = ut.unProxy(other)
        if isinstance(other, int):
            ut.ep_assert(
                self.rlocmode % other == 0,
                _("Address not divisible; {} is not a factor of {}").format(other, self.rlocmode),
            )
            return self.offset % other
        return NotImplemented

    def __neg__(self) -> "ConstExpr":
        return self.__mul__(-1)  # type: ignore[return-value]

    def __eq__(self, other) -> bool:
        if _total_ord(self, other):
            return (self.offset == other.offset) and (self.rlocmode == other.rlocmode)
        return NotImplemented

    def __hash__(self) -> int:
        return id(self)

    def __ne__(self, other) -> bool:
        if _total_ord(self, other):
            return (self.offset != other.offset) or (self.rlocmode != other.rlocmode)
        return NotImplemented

    def __lt__(self, other: "ConstExpr") -> bool:
        if _total_ord(self, other) and (self.rlocmode == other.rlocmode):
            return self.offset < other.offset
        return NotImplemented

    def __gt__(self, other: "ConstExpr") -> bool:
        if _total_ord(self, other) and (self.rlocmode == other.rlocmode):
            return self.offset > other.offset
        return NotImplemented

    def __le__(self, other: "ConstExpr") -> bool:
        if _total_ord(self, other) and (self.rlocmode == other.rlocmode):
            return self.offset <= other.offset
        return NotImplemented

    def __ge__(self, other: "ConstExpr") -> bool:
        if _total_ord(self, other) and (self.rlocmode == other.rlocmode):
            return self.offset >= other.offset
        return NotImplemented


def _total_ord(a, b) -> bool:
    if isinstance(a, ConstExpr) and isinstance(b, ConstExpr) and a.baseobj is b.baseobj:
        return True
    return False


class ConstExprInt(ConstExpr):
    def __init__(self, value: int) -> None:
        super().__init__(None, value, 0)
        self.value: RlocInt_C = RlocInt_C(value & 0xFFFFFFFF, 0)

    def Evaluate(self) -> RlocInt_C:
        return self.value


_ConstExpr = TypeVar("_ConstExpr", bound=ConstExpr)
_ExprProxy = TypeVar("_ExprProxy", bound="ExprProxy")
T = TypeVar("T", ConstExpr, int, "ExprProxy")


class Forward(ConstExpr):
    """Class for forward definition."""

    def __init__(self) -> None:
        super().__init__(self)
        self._expr: "ConstExpr | ExprProxy | None" = None
        self.dontFlatten = True

    @overload
    def __lshift__(self, expr: _ConstExpr) -> _ConstExpr:
        ...

    @overload
    def __lshift__(self, expr: _ExprProxy) -> _ExprProxy:
        ...

    @overload
    def __lshift__(self, expr: int) -> int:
        ...

    def __lshift__(self, expr: T) -> T:
        if self._expr is not None:
            raise ut.EPError(_("Reforwarding without reset is not allowed"))
        if expr is None:
            raise ut.EPError(_("Cannot forward to None"))
        if isinstance(expr, int):
            self._expr = ConstExprInt(expr)
        else:
            unproxy_expr = ut.unProxy(expr)
            if isinstance(unproxy_expr, int):
                self._expr = ConstExprInt(unproxy_expr)
            else:
                self._expr = expr
        return expr

    def IsSet(self) -> bool:
        return self._expr is not None

    def Reset(self) -> None:
        self._expr = None

    def Evaluate(self) -> RlocInt_C:
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

    def __setitem__(self, name, newvalue) -> None:
        if self._expr is None:
            raise ut.EPError(_("Forward not initialized"))
        self._expr[name] = newvalue  # type: ignore[index]


Evaluable: TypeAlias = "ConstExpr | int | ExprProxy | RlocInt_C"


def Evaluate(x: Evaluable) -> RlocInt_C:
    """Evaluate expressions"""
    expr = ut.unProxy(x)
    if isinstance(expr, ConstExpr):
        return expr.Evaluate()
    if isinstance(expr, (int, RlocInt_C)):
        return toRlocInt(expr)
    if x is expr:
        raise AttributeError(_("{} is not ConstExpr").format(x))
    raise AttributeError(_("ExprProxy {} does not wrap ConstExpr: {}").format(x, expr))


def IsConstExpr(x) -> bool:
    return isinstance(ut.unProxy(x), (ConstExpr, int, RlocInt_C))
