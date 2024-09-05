#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta
from typing import TYPE_CHECKING, TypeAlias, TypeVar

from ...localize import _
from ...utils import EPError, ExprProxy

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from ..variable import EUDVariable

Dword: TypeAlias = "int | EUDVariable | ConstExpr | ExprProxy[int] | ExprProxy[EUDVariable] | ExprProxy[ConstExpr]"  # noqa: E501
Word: TypeAlias = "int | EUDVariable | ExprProxy[int] | ExprProxy[EUDVariable]"
Byte: TypeAlias = "int | EUDVariable | ExprProxy[int] | ExprProxy[EUDVariable]"


class ConstType(ExprProxy, metaclass=ABCMeta):
    __slots__ = ()

    @classmethod
    def cast(cls, _from):
        if isinstance(_from, cls):
            return _from
        if isinstance(_from, ConstType):
            raise EPError(
                _('[Warning] "{}" is not a {}').format(_from, cls.__name__)
            )
        return cls(_from)


# return types
_Dword: TypeAlias = "int | EUDVariable | ConstExpr"
_Word: TypeAlias = "int | EUDVariable"
_Byte: TypeAlias = "int | EUDVariable"

# argument types
T = TypeVar("T", int, "EUDVariable", "ConstExpr")
U = TypeVar("U", int, "EUDVariable")
_ExprProxy: TypeAlias = (
    "ExprProxy[ConstType | int | EUDVariable | ConstExpr | ExprProxy]"
)
_Arg: TypeAlias = "ConstType | int | EUDVariable | ConstExpr | ExprProxy[ConstType | int | EUDVariable | ConstExpr | ExprProxy]"  # noqa: E501
__ExprProxy: TypeAlias = "ExprProxy[ConstType | int | EUDVariable | ExprProxy]"
__Arg: TypeAlias = "ConstType | int | EUDVariable | ExprProxy[ConstType | int | EUDVariable | ExprProxy]"  # noqa: E501
