#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TypeAlias, TypeVar, overload

from ... import utils as ut
from ...localize import _
from .rlocint import RlocInt_C, toRlocInt


class ConstExpr:
    """Class for general expression with rlocints."""

    def __init__(
        self,
        baseobj: "ConstExpr | None",
        offset: int = 0,
        rlocmode: int = 4,
    ) -> None:
        self.baseobj: "ConstExpr | None" = baseobj if rlocmode else None
        self.offset: int = offset
        self.rlocmode: int = rlocmode

    def Evaluate(self) -> RlocInt_C:  # noqa: N802
        if self.baseobj is not None:
            return self.baseobj.Evaluate() * self.rlocmode // 4 + self.offset  # type: ignore[union-attr]
        else:
            return RlocInt_C(self.offset, 0)

    def __add__(self, other: "int | ConstExpr") -> "ConstExpr":
        if isinstance(other, int):
            return ConstExpr(self.baseobj, self.offset + other, self.rlocmode)
        if isinstance(other, ConstExpr):
            offset = self.offset + other.offset
            if self.rlocmode == 0:
                return ConstExpr(other.baseobj, offset, other.rlocmode)
            if other.rlocmode == 0:
                return ConstExpr(self.baseobj, offset, self.rlocmode)
            if self.baseobj is other.baseobj:
                rlocmode = self.rlocmode + other.rlocmode
                return ConstExpr(self.baseobj, offset, rlocmode)
        return NotImplemented

    def __radd__(self, other: "int | ConstExpr") -> "ConstExpr":
        return self.__add__(other)

    def __sub__(self, other: "int | ConstExpr") -> "ConstExpr":
        if isinstance(other, int):
            return ConstExpr(self.baseobj, self.offset - other, self.rlocmode)
        if isinstance(other, ConstExpr):
            offset = self.offset - other.offset
            if self.rlocmode == 0:
                return ConstExpr(other.baseobj, offset, -other.rlocmode)
            if other.rlocmode == 0:
                return ConstExpr(self.baseobj, offset, self.rlocmode)
            if self.baseobj is other.baseobj:
                rlocmode = self.rlocmode - other.rlocmode
                return ConstExpr(self.baseobj, offset, rlocmode)
        return NotImplemented

    def __rsub__(self, other: "int | ConstExpr") -> "ConstExpr":
        if isinstance(other, int):
            return ConstExpr(self.baseobj, other - self.offset, -self.rlocmode)
        if isinstance(other, ConstExpr):
            offset = other.offset - self.offset
            if self.rlocmode == 0:
                return ConstExpr(other.baseobj, offset, other.rlocmode)
            if other.rlocmode == 0:
                return ConstExpr(self.baseobj, offset, -self.rlocmode)
            if self.baseobj is other.baseobj:
                rlocmode = other.rlocmode - self.rlocmode
                return ConstExpr(self.baseobj, offset, rlocmode)
        return NotImplemented

    def __mul__(self, other: int) -> "ConstExpr":
        if isinstance(other, int):
            return ConstExpr(
                self.baseobj, self.offset * other, self.rlocmode * other
            )
        return NotImplemented

    def __rmul__(self, other: "int") -> "ConstExpr":
        return self.__mul__(other)

    def __floordiv__(self, other: "int") -> "ConstExpr":
        if isinstance(other, int):
            ut.ep_assert(
                self.rlocmode % other == 0,
                _("Address not divisible; {} is not a factor of {}").format(
                    other, self.rlocmode
                ),
            )
            return ConstExpr(
                self.baseobj, self.offset // other, self.rlocmode // other
            )
        return NotImplemented

    def __mod__(self, other: "int") -> int:
        if isinstance(other, int):
            ut.ep_assert(
                self.rlocmode % other == 0,
                _("Address not divisible; {} is not a factor of {}").format(
                    other, self.rlocmode
                ),
            )
            return self.offset % other
        return NotImplemented

    def __neg__(self) -> "ConstExpr":
        return self.__mul__(-1)

    def __eq__(self, other: "int | ConstExpr") -> bool:
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset == other
        if isinstance(other, ConstExpr) and self.baseobj is other.baseobj:
            return (self.offset == other.offset) and (
                self.rlocmode == other.rlocmode
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((id(self.baseobj), self.offset, self.rlocmode))

    def __ne__(self, other: "int | ConstExpr") -> bool:
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset != other
        if isinstance(other, ConstExpr) and self.baseobj is other.baseobj:
            return (self.offset != other.offset) or (self.rlocmode != other.rlocmode)
        return NotImplemented

    def __lt__(self, other: "int | ConstExpr") -> bool:
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset < other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset < other.offset
        return NotImplemented

    def __gt__(self, other: "ConstExpr | int") -> bool:
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset > other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset > other.offset
        return NotImplemented

    def __le__(self, other: "ConstExpr | int") -> bool:
        if isinstance(other, int) and self.rlocmode == 0:
            return self.offset <= other
        if (
            isinstance(other, ConstExpr)
            and self.baseobj is other.baseobj
            and (self.rlocmode == other.rlocmode)
        ):
            return self.offset <= other.offset
        return NotImplemented

    def __ge__(self, other: "ConstExpr | int") -> bool:
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


_ConstExpr = TypeVar("_ConstExpr", bound=ConstExpr)


class Forward(ConstExpr):
    """Class for forward definition."""

    def __init__(self) -> None:
        super().__init__(self)
        self._expr: ConstExpr | None = None

    @overload
    def __lshift__(self, expr: _ConstExpr) -> _ConstExpr:
        ...

    @overload
    def __lshift__(self, expr: ut.ExprProxy[_ConstExpr]) -> ut.ExprProxy[_ConstExpr]:
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

    def IsSet(self) -> bool:  # noqa: N802
        return self._expr is not None

    def Reset(self) -> None:  # noqa: N802
        self._expr = None

    def Evaluate(self) -> RlocInt_C:  # noqa: N802
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
        return self._expr[name]

    def __setitem__(self, name, newvalue):
        self._expr[name] = newvalue


Evaluable: TypeAlias = ConstExpr | int | ut.ExprProxy[ConstExpr] | RlocInt_C


def Evaluate(x: Evaluable) -> RlocInt_C:  # noqa: N802
    """Evaluate expressions"""
    expr = ut.unProxy(x)
    if isinstance(expr, ConstExpr):
        return expr.Evaluate()
    if isinstance(expr, (int, RlocInt_C)):
        return toRlocInt(expr)
    if x is expr:
        raise AttributeError(
            _("Only ConstExpr can be Evaluated, not {}").format(repr(x))
        )
    raise AttributeError(
        _("ExprProxy {} does not wrap ConstExpr, instead {}").format(x, repr(expr))
    )


def IsConstExpr(x) -> bool:  # noqa: N802
    return isinstance(ut.unProxy(x), (ConstExpr, int, RlocInt_C))
