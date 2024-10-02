# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta
from typing import TYPE_CHECKING, TypeAlias, TypeVar

from typing_extensions import Self

from ...localize import _
from ...utils import EPError, ExprProxy

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from ..variable import EUDVariable

Dword: TypeAlias = (
    "int | EUDVariable | ConstExpr | ExprProxy[int | EUDVariable | ConstExpr]"
)
Word: TypeAlias = "int | EUDVariable | ExprProxy[int | EUDVariable]"
Byte: TypeAlias = "int | EUDVariable | ExprProxy[int | EUDVariable]"


class ConstType(ExprProxy, metaclass=ABCMeta):
    __slots__ = ()

    @classmethod
    def cast(cls, _from):
        if isinstance(_from, cls):
            return _from
        if isinstance(_from, ConstType):
            raise EPError(_('"{}" is not a {}').format(_from, cls.__name__))
        return cls(_from)

    def _check_assign(self, other) -> None:
        from ..variable import EUDVariable

        if not isinstance(self._value, EUDVariable):
            raise EPError(_("Can't assign {} to constant expression").format(other))
        if type(other) is ExprProxy:
            other = other._value
        if isinstance(other, type(self)):
            return
        if isinstance(other, int | EUDVariable | str):
            return
        else:
            raise EPError(_("Can't assign {} to {}").format(other, self))

    def Assign(self, other) -> Self:  # noqa: N802
        self._check_assign(other)
        other = type(self).cast(other)
        self._value.Assign(other)
        return self

    def __iadd__(self, other) -> Self:
        self._check_assign(other)
        self._value.__iadd__(other)
        return self

    def __isub__(self, other) -> Self:
        self._check_assign(other)
        self._value.__isub__(other)
        return self

    def __ior__(self, other) -> Self:
        self._check_assign(other)
        self._value.__ior__(other)
        return self

    def __iand__(self, other) -> Self:
        self._check_assign(other)
        self._value.__iand__(other)
        return self

    def __ixor__(self, other) -> Self:
        self._check_assign(other)
        self._value.__ixor__(other)
        return self

    def __imul__(self, other) -> Self:
        self._check_assign(other)
        self._value.__imul__(other)
        return self

    def __ifloordiv__(self, other) -> Self:
        self._check_assign(other)
        self._value.__ifloordiv__(other)
        return self

    def __imod__(self, other) -> Self:
        self._check_assign(other)
        self._value.__imod__(other)
        return self

    def __ilshift__(self, other) -> Self:
        self._check_assign(other)
        self._value.__ilshift__(other)
        return self

    def __irshift__(self, other) -> Self:
        self._check_assign(other)
        self._value.__irshift__(other)
        return self


# return types
_Dword: TypeAlias = "int | EUDVariable | ConstExpr"
_Word: TypeAlias = "int | EUDVariable"
_Byte: TypeAlias = "int | EUDVariable"

# argument types
T = TypeVar("T", int, "EUDVariable", "ConstExpr")
U = TypeVar("U", int, "EUDVariable")
_ExprProxy: TypeAlias = (
    "ExprProxy[ConstType | int | EUDVariable | ConstExpr | _ExprProxy]"
)
_Arg: TypeAlias = "ConstType | int | EUDVariable | ConstExpr | ExprProxy[_Arg]"
__ExprProxy: TypeAlias = "ExprProxy[ConstType | int | EUDVariable | __ExprProxy]"
__Arg: TypeAlias = "ConstType | int | EUDVariable | ExprProxy[__Arg]"
