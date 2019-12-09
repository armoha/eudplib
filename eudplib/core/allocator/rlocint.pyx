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

from eudplib import utils as ut
from eudplib.localize import _


cdef class RlocInt_C:

    """Relocatable int"""

    def __cinit__(self, size_t offset, size_t rlocmode):
        self.offset, self.rlocmode = offset, rlocmode

    # http://stackoverflow.com/questions/18794169/pythons-radd-doesnt-work-for-c-defined-types
    # Some obscure type can fludge into 'self' slot, so I called it'lhs'
    # rather than self.
    def __add__(lhs, rhs):
        if isinstance(lhs, RlocInt_C):  # Call from radd
            if isinstance(rhs, RlocInt_C):
                return RlocInt_C(
                    lhs.offset + rhs.offset,
                    lhs.rlocmode + rhs.rlocmode
                )
            else:
                return RlocInt_C(
                    (lhs.offset + rhs) & 0xFFFFFFFF,
                    lhs.rlocmode
                )
        else:
            return RlocInt_C(
                (rhs.offset + lhs) & 0xFFFFFFFF,
                rhs.rlocmode
            )

    def __sub__(lhs, rhs):
        lhs = toRlocInt(lhs)
        if isinstance(rhs, RlocInt_C):
            return RlocInt_C(
                (lhs.offset - rhs.offset) & 0xFFFFFFFF,
                (lhs.rlocmode - rhs.rlocmode) & 0xFFFFFFFF
            )
        else:
            return RlocInt_C(
                (lhs.offset - rhs) & 0xFFFFFFFF,
                lhs.rlocmode
            )

    def __mul__(self, other):
        if isinstance(other, RlocInt_C):
            ut.ep_assert(
                other.rlocmode == 0,
                _('Cannot divide RlocInt with non-const')
            )
            other = other.offset

        return RlocInt_C(
            (self.offset * other) & 0xFFFFFFFF,
            self.rlocmode * other
        )

    def __floordiv__(self, other):
        if isinstance(other, RlocInt_C):
            ut.ep_assert(
                other.rlocmode == 0,
                _('Cannot divide RlocInt with non-const')
            )
            other = other.offset
        ut.ep_assert(other != 0, _('Divide by zero'))
        ut.ep_assert(
            (self.rlocmode == 0) or (self.rlocmode % other == 0 and self.offset % other == 0),
            _('RlocInt not divisible by {}').format(other)
        )
        return RlocInt_C(
            (self.offset // other) & 0xFFFFFFFF,
            self.rlocmode // other
        )

    def __str__(self):
        return 'RlocInt(0x%08X, %d)' % (self.offset, self.rlocmode)

    def __repr__(self):
        return str(self)


cpdef RlocInt_C RlocInt(offset, rlocmode):
    return RlocInt_C(offset & 0xFFFFFFFF, rlocmode & 0xFFFFFFFF)

cpdef RlocInt_C toRlocInt(x):
    """Convert int/RlocInt to rlocint"""

    if isinstance(x, RlocInt_C):
        return x

    else:
        return RlocInt_C(x & 0xFFFFFFFF, 0)
