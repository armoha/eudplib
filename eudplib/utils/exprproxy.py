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

from eudplib.localize import _


class ExprProxy:

    """Class which can contain both ConstExpr and EUDVariable"""

    def __init__(self, initval):
        self._value = initval

    @classmethod
    def cast(cls, _from):
        try:
            return cls(_from=_from)
        except TypeError as e:
            raise TypeError(_("Type {} is not castable").format(cls.__name__), e)

    def getValue(self):
        return self._value

    def __hash__(self):
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

    # TODO: add AttrProxy for specialized in-place operations and comparison
    def __getattr__(self, name):
        return getattr(self._value, name)

    def __getitem__(self, name):
        return ItemProxy(self._value, name)

    def __iter__(self):
        return self._value

    def __setitem__(self, name, newvalue):
        self._value[name] = newvalue


def unProxy(x):
    try:
        return unProxy(x.getValue())
    except AttributeError:
        return x


def isUnproxyInstance(x, cls):
    if isinstance(x, cls):
        return True
    try:
        return isUnproxyInstance(x.getValue(), cls)
    except (AttributeError, TypeError):
        return False


class ItemProxy:
    def __init__(self, parent, key):
        self._parent = parent
        self._key = key
        self._value = None

    @classmethod
    def cast(cls, _from):
        try:
            return cls(_from=_from)
        except TypeError as e:
            raise TypeError(_("Type {} is not castable").format(cls.__name__), e)

    def getValue(self):
        if self._value is None:
            from ..core.variable import EUDVariable

            self._value = self._parent[self._key]
            self.__class__ = EUDVariable
            self._vartrigger = self._value._vartrigger
            self._varact = self._value._varact
            self._rvalue = self._value._rvalue
        return self._value

    def __hash__(self):
        return id(self)

    # in-place item operations
    # FIXME: should we raise AttributeError for unsupported arguments?
    def __iadd__(self, v):
        try:
            self._parent.iadditem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov += v
            self._parent[self._key] = ov
        return self

    def __isub__(self, v):
        try:
            self._parent.isubitem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov -= v
            self._parent[self._key] = ov
        return self

    def __imul__(self, v):
        try:
            self._parent.imulitem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov *= v
            self._parent[self._key] = ov
        return self

    def __ifloordiv__(self, v):
        try:
            self._parent.ifloordivitem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov //= v
            self._parent[self._key] = ov
        return self

    def __imod__(self, v):
        try:
            self._parent.imoditem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov %= v
            self._parent[self._key] = ov
        return self

    def __ilshift__(self, v):
        try:
            self._parent.ilshiftitem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov <<= v
            self._parent[self._key] = ov
        return self

    def __irshift__(self, v):
        try:
            self._parent.irshiftitem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov >>= v
            self._parent[self._key] = ov
        return self

    def __ipow__(self, v):
        try:
            self._parent.ipowitem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov **= v
            self._parent[self._key] = ov
        return self

    def __iand__(self, v):
        try:
            self._parent.ianditem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov &= v
            self._parent[self._key] = ov
        return self

    def __ior__(self, v):
        try:
            self._parent.ioritem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov |= v
            self._parent[self._key] = ov
        return self

    def __ixor__(self, v):
        try:
            self._parent.ixoritem(self._key, v)
        except AttributeError:
            ov = self.getValue()
            ov ^= v
            self._parent[self._key] = ov
        return self

    # Proxy arithmetic operators

    def __lshift__(self, k):
        return self.getValue() << k

    def __rlshift__(self, k):
        return k << self.getValue()

    def __rshift__(self, k):
        return self.getValue() >> k

    def __rrshift__(self, k):
        return k >> self.getValue()

    def __add__(self, k):
        return self.getValue() + k

    def __radd__(self, k):
        return k + self.getValue()

    def __sub__(self, k):
        return self.getValue() - k

    def __rsub__(self, k):
        return k - self.getValue()

    def __mul__(self, k):
        return self.getValue() * k

    def __rmul__(self, k):
        return k * self.getValue()

    def __floordiv__(self, k):
        return self.getValue() // k

    def __rfloordiv__(self, k):
        return k // self.getValue()

    def __mod__(self, k):
        return self.getValue() % k

    def __rmod__(self, k):
        return k % self.getValue()

    def __and__(self, k):
        return self.getValue() & k

    def __rand__(self, k):
        return k & self.getValue()

    def __or__(self, k):
        return self.getValue() | k

    def __ror__(self, k):
        return k | self.getValue()

    def __xor__(self, k):
        return self.getValue() ^ k

    def __rxor__(self, k):
        return k ^ self.getValue()

    def __neg__(self):
        return -self.getValue()

    def __invert__(self):
        return ~self.getValue()

    # Proxy comparison operator

    def __eq__(self, k):
        if self._value is None:
            try:
                return self._parent.eqitem(self._key, k)
            except AttributeError:
                pass
        return self.getValue() == k

    def __ne__(self, k):
        if self._value is None:
            try:
                return self._parent.neitem(self._key, k)
            except AttributeError:
                pass
        return self.getValue() != k

    def __le__(self, k):
        if self._value is None:
            try:
                return self._parent.leitem(self._key, k)
            except AttributeError:
                pass
        return self.getValue() <= k

    def __lt__(self, k):
        if self._value is None:
            try:
                return self._parent.ltitem(self._key, k)
            except AttributeError:
                pass
        return self.getValue() < k

    def __ge__(self, k):
        if self._value is None:
            try:
                return self._parent.geitem(self._key, k)
            except AttributeError:
                pass
        return self.getValue() >= k

    def __gt__(self, k):
        if self._value is None:
            try:
                return self._parent.gtitem(self._key, k)
            except AttributeError:
                pass
        return self.getValue() > k

    def __bool__(self):
        if self._value is None:
            try:
                return self._parent.boolitem(self._key, k)
            except AttributeError:
                pass
        return bool(self.getValue())
