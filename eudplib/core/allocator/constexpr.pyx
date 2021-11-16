#!/usr/bin/python
# -*- coding: utf-8 -*-
# cython: language_level=3

'''
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
'''

from .rlocint cimport RlocInt_C, toRlocInt
from .rlocint import RlocInt, RlocInt_C, toRlocInt
from ... import utils as ut
from ...localize import _


cdef class ConstExpr:

    ''' Class for general expression with rlocints.
    '''

    cdef public unsigned int offset, rlocmode
    cdef public ConstExpr baseobj

    def __init__(self, baseobj, offset=0, rlocmode=4):
        self.baseobj = baseobj
        self.offset = offset & 0xFFFFFFFF
        self.rlocmode = rlocmode & 0xFFFFFFFF

    cpdef RlocInt_C Evaluate(self):
        return self.baseobj.Evaluate() * self.rlocmode // 4 + self.offset

    def _total_ord(self, other):
        if isinstance(other, ConstExpr) and self.baseobj is other.baseobj:
            return True
        return False

    # Cython version!

    def __add__(self, other):
        if self._total_ord(other):
            if self.rlocmode + other.rlocmode == 0:
                return self.offset + other.offset
            return ConstExpr(
                self.baseobj, self.offset + other.offset, self.rlocmode + other.rlocmode
            )
        elif not isinstance(other, int):
            return NotImplemented

        return ConstExpr(self.baseobj, self.offset + other, self.rlocmode)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if self._total_ord(other):
            if self.rlocmode == other.rlocmode:
                return self.offset - other.offset
            return ConstExpr(
                self.baseobj, self.offset - other.offset, self.rlocmode - other.rlocmode
            )
        elif not isinstance(other, int):
            return NotImplemented

        return ConstExpr(self.baseobj, self.offset - other, self.rlocmode)

    def __rsub__(self, other):
        if self._total_ord(other):
            if self.rlocmode == other.rlocmode:
                return other.offset - self.offset
            return ConstExpr(
                self.baseobj, other.offset - self.offset, other.rlocmode - self.rlocmode
            )
        elif not isinstance(other, int):
            return NotImplemented

        return ConstExpr(self.baseobj, other - self.offset, -self.rlocmode)

    def __mul__(self, k):
        if not isinstance(k, int):
            return NotImplemented

        return ConstExpr(self.baseobj, self.offset * k, self.rlocmode * k)

    def __rmul__(self, k):
        if not isinstance(k, int):
            return NotImplemented

        return ConstExpr(self.baseobj, self.offset * k, self.rlocmode * k)

    def __floordiv__(self, k):
        if not isinstance(k, int):
            return NotImplemented
        ut.ep_assert(
            (self.rlocmode == 0) or (self.rlocmode % k == 0),
            _("Address not divisible; {} is not a factor of {}").format(
                k, self.rlocmode
            ),
        )
        return ConstExpr(self.baseobj, self.offset // k, self.rlocmode // k)

    def __mod__(self, k):
        if not isinstance(k, int):
            return NotImplemented
        ut.ep_assert(4 % k == 0 and self.rlocmode == 4)
        return self.offset % k

    def __neg__(self):
        return self.__mul__(-1)

    def __eq__(self, other):
        if self._total_ord(other):
            return (self.offset == other.offset) and (self.rlocmode == other.rlocmode)
        return NotImplemented

    def __hash__(self):
        return id(self)

    def __ne__(self, other):
        if self._total_ord(other):
            return (self.offset != other.offset) or (self.rlocmode != other.rlocmode)
        return NotImplemented

    def __lt__(self, other):
        if self._total_ord(other) and (self.rlocmode == other.rlocmode):
            return self.offset < other.offset
        return NotImplemented

    def __gt__(self, other):
        if self._total_ord(other) and (self.rlocmode == other.rlocmode):
            return self.offset > other.offset
        return NotImplemented

    def __le__(self, other):
        if self._total_ord(other) and (self.rlocmode == other.rlocmode):
            return self.offset <= other.offset
        return NotImplemented

    def __ge__(self, other):
        if self._total_ord(other) and (self.rlocmode == other.rlocmode):
            return self.offset >= other.offset
        return NotImplemented


cdef class ConstExprInt(ConstExpr):
    cdef public RlocInt_C value

    def __init__(self, value):
        super().__init__(None, value, 0)
        self.value = RlocInt_C(value & 0xFFFFFFFF, 0)

    cpdef RlocInt_C Evaluate(self):
        return self.value

cdef class Forward(ConstExpr):

    '''Class for forward definition.
    '''

    cdef public ConstExpr _expr

    def __init__(self):
        super().__init__(self)
        self._expr = None

    def __lshift__(self, expr):
        ut.ep_assert(
            self._expr is None,
            _('Reforwarding without reset is not allowed')
        )
        expr = ut.unProxy(expr)
        ut.ep_assert(expr is not None, _('Cannot forward to None'))
        if isinstance(expr, int):
            self._expr = ConstExprInt(expr)
        else:
            self._expr = expr
        return expr

    def IsSet(self):
        return self._expr is not None

    def Reset(self):
        self._expr = None

    cpdef RlocInt_C Evaluate(self):
        ut.ep_assert(self._expr is not None, _('Forward not initialized'))
        return self._expr.Evaluate()

    def __call__(self, *args, **kwargs):
        return self._expr(*args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._expr, name)

    def __getitem__(self, name):
        return self._expr[name]

    def __setitem__(self, name, newvalue):
        self._expr[name] = newvalue


cpdef RlocInt_C Evaluate(x):
    '''
    Evaluate expressions
    '''
    try:
        return x.Evaluate()
    except AttributeError:
        try:
            return toRlocInt(x)
        except TypeError:
            raise ut.EPError(_("Cannot evaluate value '{}'").format(x))


def IsConstExpr(x):
    x = ut.unProxy(x)
    return isinstance(x, int) or isinstance(x, RlocInt_C) or hasattr(x, 'Evaluate')
