#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import types
from typing import Any, Generic, TypeAlias, TypeVar, overload

from eudplib.localize import _

T_co = TypeVar("T_co", covariant=True)


class ExprProxy(Generic[T_co]):
    """Class which can contain both ConstExpr and EUDVariable"""

    def __init__(self, initval: T_co) -> None:
        self._value: T_co = initval

    @classmethod
    def cast(cls, _from):
        try:
            return cls(_from=_from)
        except TypeError as e:
            raise TypeError(_("Type {} is not castable").format(cls.__name__), e)

    def getValue(self) -> T_co:
        return self._value

    def __len__(self):
        return len(self._value)

    def __hash__(self) -> int:
        return id(self)

    # Forbid in-place operators

    def __iadd__(self, k):
        raise AttributeError

    def __iand__(self, k):
        raise AttributeError

    def __iconcat__(self, k):
        raise AttributeError

    def __ifloordiv__(self, k):
        raise AttributeError

    def __ilshift__(self, k):
        raise AttributeError

    def __imod__(self, k):
        raise AttributeError

    def __imul__(self, k):
        raise AttributeError

    def __imatmul__(self, k):
        raise AttributeError

    def __ior__(self, k):
        raise AttributeError

    def __ipow__(self, k):
        raise AttributeError

    def __irshift__(self, k):
        raise AttributeError

    def __isub__(self, k):
        raise AttributeError

    def __itruediv__(self, k):
        raise AttributeError

    def __ixor__(self, k):
        raise AttributeError

    # Proxy arithmetic operators

    def __lshift__(self, k):
        return self._value << k

    def __rlshift__(self, k):
        return k << self._value

    def __rshift__(self, k):
        return self._value >> k

    def __rrshift__(self, k):
        return k >> self._value

    def __add__(self, k):
        return self._value + k

    def __radd__(self, k):
        return k + self._value

    def __sub__(self, k):
        return self._value - k

    def __rsub__(self, k):
        return k - self._value

    def __mul__(self, k):
        return self._value * k

    def __rmul__(self, k):
        return k * self._value

    def __floordiv__(self, k):
        return self._value // k

    def __rfloordiv__(self, k):
        return k // self._value

    def __mod__(self, k):
        return self._value % k

    def __rmod__(self, k):
        return k % self._value

    def __and__(self, k):
        return self._value & k

    def __rand__(self, k):
        return k & self._value

    def __or__(self, k):
        return self._value | k

    def __ror__(self, k):
        return k | self._value

    def __xor__(self, k):
        return self._value ^ k

    def __rxor__(self, k):
        return k ^ self._value

    def __neg__(self):
        return -self._value

    def __invert__(self):
        return ~self._value

    def __bool__(self):
        return bool(self._value)

    # Proxy comparison operator

    def __eq__(self, k):
        return self._value == k

    def __ne__(self, k):
        return self._value != k

    def __le__(self, k):
        return self._value <= k

    def __lt__(self, k):
        return self._value < k

    def __ge__(self, k):
        return self._value >= k

    def __gt__(self, k):
        return self._value > k

    # TODO: add inplace operators

    # Proxy other methods
    def __getattribute__(self, name):
        if name == "_value":
            return super().__getattribute__(name)
        elif name == "__class__":
            return object.__getattribute__(self._value, name)
        else:
            return super().__getattribute__(name)

    def __call__(self, *args, **kwargs):
        return self._value(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._value, name)

    def __getitem__(self, name):
        return self._value[name]

    def __setitem__(self, name, newvalue):
        self._value[name] = newvalue

    def __iter__(self):
        try:
            return self._value.__iter__()
        except AttributeError:
            return self._value


T = TypeVar("T")


@overload
def unProxy(x: ExprProxy[T]) -> T:
    ...


@overload
def unProxy(x: T) -> T:
    ...


def unProxy(x):
    while isinstance(x, ExprProxy):
        x = x.getValue()
    return x


_ClassInfo: TypeAlias = type | types.UnionType | tuple["_ClassInfo", ...]


def isUnproxyInstance(x: object, cls: _ClassInfo) -> bool:
    if isinstance(x, cls):
        return True
    if isinstance(unProxy(x), cls):
        return True
    return False
