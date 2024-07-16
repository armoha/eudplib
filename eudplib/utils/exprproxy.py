#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import types
from typing import Generic, TypeAlias, TypeVar, overload

from eudplib.localize import _

T_co = TypeVar("T_co", covariant=True)


class ExprProxy(Generic[T_co]):
    """Class which can contain both ConstExpr and EUDVariable"""

    __slots__ = ("_value",)

    def __init__(self, initval: T_co) -> None:
        # Python __slots__ is just a sugar for auto-generated descriptors.
        # Calling descriptors is implemented within __setattr__ and __getattr__
        # (or __*attribute__, I haven't dug deep) of object. The most importantly,
        # we have overridden the default __setattr__ and as a result, were unable to
        # initialize the value using dot notation within the ctor. Since the value of
        # the slotted variable is not yet initialized, our __setattr__ causes access
        # to __getattr__ (an incorrect behaviour by itself!), and __getattr__ needs
        # the slotted variable itself, so - infinite recursion.
        #
        # So, to initialize the value correctly, we should call the descriptor method
        # explicitly. See: https://stackoverflow.com/a/63338642
        super().__setattr__("_value", initval)
        # self._value: T_co = initval

    @classmethod
    def cast(cls, _from):
        try:
            return cls(_from=_from)
        except TypeError as e:
            raise TypeError(_("Type {} is not castable").format(cls.__name__), e)

    def getValue(self) -> T_co:  # noqa: N802
        return self._value

    def __len__(self):
        return len(self._value)

    def __hash__(self) -> int:
        return id(self)

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

    def __divmod__(self, k):
        return divmod(self._value, k)

    def __rdivmod__(self, k):
        return divmod(k, self._value)

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

    def __call__(self, *args, **kwargs):
        return self._value(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(super().__getattribute__("_value"), name)

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


def unProxy(x):  # noqa: N802
    k = 0

    # Cyclic check without using list/set
    # x_cyclic_check = ((lambda x: x.getValue) ** (2**n))(x)
    # if there is a cycle, x will go though the cycle and meet with x_cyclic_check
    # since (2**n) diverges, this code can catch cycles up to any size.
    x_cyclic_check = x0 = x
    while isinstance(x, ExprProxy):
        x = x.getValue()
        if x is x_cyclic_check:
            # Reconstruct cyclic reference
            err = _("ExprProxy {} has cyclic references: ")
            x_list = []
            x_set = set()

            x = x0
            while x not in x_set:
                x_list.append(x)
                x_set.add(x)
                x = x.getValue()

            raise RecursionError(
                err.format(x_list[0]),
                x_list,
            )

        k += 1
        # only becomes true if k == 2**i for some integer i
        if k & (k - 1) == 0:
            x_cyclic_check = x

    return x


_ClassInfo: TypeAlias = type | types.UnionType | tuple["_ClassInfo", ...]


def isUnproxyInstance(x: object, cls: _ClassInfo) -> bool:  # noqa: N802
    if isinstance(x, cls):
        return True
    if isinstance(unProxy(x), cls):
        return True
    return False
