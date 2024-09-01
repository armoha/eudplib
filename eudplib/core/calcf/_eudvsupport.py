#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable

from ..variable import EUDVariable
from .bitwise import f_bitlshift, f_bitrshift
from .muldiv import _quot, _rem, f_mul


def _def_cls_method(name: str, f: Callable) -> None:
    f.__name__ = f"EUDVariable.{name}"
    setattr(EUDVariable, name, f)


def _def_bin_operator(name: str, f: Callable) -> None:
    _def_cls_method(name, f)
    _def_cls_method(f"__r{name[2:]}", lambda self, lhs: f(lhs, self))


def _def_inplace_operator(name: str, f: Callable) -> None:
    def iop(self, other):
        rvalue = self._rvalue
        ret = f(self, other)
        if not rvalue:
            ret.makeL()
        return ret

    _def_cls_method(name, iop)


_def_bin_operator("__mul__", lambda x, y: f_mul(x, y))
_def_bin_operator("__floordiv__", lambda x, y: _quot(x, y))
_def_bin_operator("__mod__", lambda x, y: _rem(x, y))
_def_bin_operator("__rshift__", lambda x, y: f_bitrshift(x, y))
_def_inplace_operator("__imul__", lambda x, y: f_mul(x, y, ret=[x]))
_def_inplace_operator("__ifloordiv__", lambda x, y: _quot(x, y, ret=[x]))
_def_inplace_operator("__imod__", lambda x, y: _rem(x, y, ret=[x]))
_def_inplace_operator("__ilshift__", lambda a, b: f_bitlshift(a, b, ret=[a]))
_def_inplace_operator("__irshift__", lambda a, b: f_bitrshift(a, b, ret=[a]))
_def_cls_method("__rlshift__", lambda a, b: f_bitlshift(b, a))

# Shift operator is reserved for assigning, so we won't overload them.
