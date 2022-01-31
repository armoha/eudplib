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

from .muldiv import f_mul, f_div
from .bitwise import f_bitand, f_bitor, f_bitxor, f_bitnot, f_bitlshift, f_bitrshift


from ..variable import EUDVariable
from ..variable.evcommon import _ev


def DefClsMethod(name, f):
    f.__name__ = "EUDVariable.%s" % name
    setattr(EUDVariable, name, f)


def DefBinOperator(name, f):
    DefClsMethod(name, f)

    def rop(self, lhs):
        return f(lhs, self)

    DefClsMethod("__r%s" % name[2:], rop)


def DefOperator(name, f):
    DefBinOperator(name, f)

    def iop(self, rhs):
        self << f(self, rhs)
        return self

    DefClsMethod("__i%s" % name[2:], iop)


DefBinOperator("__mul__", lambda x, y: f_mul(x, y))
DefBinOperator("__floordiv__", lambda x, y: f_div(x, y)[0])
DefBinOperator("__mod__", lambda x, y: f_div(x, y)[1])
DefClsMethod("__imul__", lambda x, y: f_mul(x, y, ret=[x]))
DefClsMethod("__ifloordiv__", lambda x, y: f_div(x, y, ret=[x, _ev[4]])[0])
DefClsMethod("__imod__", lambda x, y: f_div(x, y, ret=[_ev[4], x])[1])
DefBinOperator("__and__", lambda x, y: f_bitand(x, y))
DefBinOperator("__or__", lambda x, y: f_bitor(x, y))
DefOperator("__xor__", lambda x, y: f_bitxor(x, y))  # FIXME
DefClsMethod("__neg__", lambda x: 0 - x)
DefClsMethod("__invert__", lambda x: f_bitnot(x))
DefClsMethod("__ilshift__", lambda a, b: f_bitlshift(a, b, ret=[a]))  # FIXME
DefClsMethod("__irshift__", lambda a, b: f_bitrshift(a, b, ret=[a]))  # FIXME
DefClsMethod("__rlshift__", lambda a, b: f_bitlshift(b, a))
DefClsMethod("__rrshift__", lambda a, b: f_bitrshift(b, a))

# Shift operator is reserved for assigning, so we won't overload them.
