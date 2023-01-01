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

from collections.abc import Callable

from ..variable import EUDVariable
from ..variable.evcommon import _ev
from .bitwise import f_bitand, f_bitlshift, f_bitnot, f_bitor, f_bitrshift, f_bitxor
from .muldiv import f_div, f_mul


def DefClsMethod(name: str, f: Callable) -> None:
    f.__name__ = "EUDVariable.%s" % name
    setattr(EUDVariable, name, f)


def DefBinOperator(name: str, f: Callable) -> None:
    DefClsMethod(name, f)
    DefClsMethod("__r%s" % name[2:], lambda self, lhs: f(lhs, self))


def DefInplaceOperator(name: str, f: Callable) -> None:
    def iop(self, other):
        rvalue = self._rvalue
        ret = f(self, other)
        if not rvalue:
            ret.makeL()
        return ret

    DefClsMethod(name, iop)


DefBinOperator("__mul__", lambda x, y: f_mul(x, y))
DefBinOperator("__floordiv__", lambda x, y: f_div(x, y)[0])
DefBinOperator("__mod__", lambda x, y: f_div(x, y)[1])
DefBinOperator("__rshift__", lambda x, y: f_bitrshift(x, y))
DefInplaceOperator("__imul__", lambda x, y: f_mul(x, y, ret=[x]))
DefInplaceOperator("__ifloordiv__", lambda x, y: f_div(x, y, ret=[x, _ev[4]])[0])
DefInplaceOperator("__imod__", lambda x, y: f_div(x, y, ret=[_ev[4], x])[1])
DefInplaceOperator("__ilshift__", lambda a, b: f_bitlshift(a, b, ret=[a]))
DefInplaceOperator("__irshift__", lambda a, b: f_bitrshift(a, b, ret=[a]))  # FIXME
DefClsMethod("__rlshift__", lambda a, b: f_bitlshift(b, a))

# Shift operator is reserved for assigning, so we won't overload them.
