#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Callable

from ..variable import EUDVariable
from ..variable.evcommon import _ev
from .bitwise import f_bitlshift, f_bitrshift
from .muldiv import f_mul, _quot, _rem


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
DefBinOperator("__floordiv__", lambda x, y: _quot(x, y))
DefBinOperator("__mod__", lambda x, y: _rem(x, y))
DefBinOperator("__rshift__", lambda x, y: f_bitrshift(x, y))
DefInplaceOperator("__imul__", lambda x, y: f_mul(x, y, ret=[x]))
DefInplaceOperator("__ifloordiv__", lambda x, y: _quot(x, y, ret=[x]))
DefInplaceOperator("__imod__", lambda x, y: _rem(x, y, ret=[x]))
DefInplaceOperator("__ilshift__", lambda a, b: f_bitlshift(a, b, ret=[a]))
DefInplaceOperator("__irshift__", lambda a, b: f_bitrshift(a, b, ret=[a]))  # FIXME
DefClsMethod("__rlshift__", lambda a, b: f_bitlshift(b, a))

# Shift operator is reserved for assigning, so we won't overload them.
