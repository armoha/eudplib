#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
import inspect
from collections.abc import Callable

from ... import utils as ut
from ...localize import _
from .. import variable as ev
from ..eudstruct.eudstruct import EUDStruct
from ..eudstruct.selftype import _set_selftype, selftype
from .eudtypedfuncn import EUDTypedFuncN, _apply_types_to_fargs

_mth_classtype: dict[Callable, type] = {}


def EUDTypedMethod(argtypes, rettypes=None, *, traced=False):  # noqa: N802
    def _eud_typed_method(method):
        # Get argument number of fdecl_func
        argspec = inspect.getfullargspec(method)
        ut.ep_assert(
            argspec[1] is None,
            _("No variadic arguments (*args) allowed for EUDFunc."),
        )
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
        )

        # Get number of arguments excluding self
        argn = len(argspec[0]) - 1

        constexpr_callmap = {}

        # Generic caller
        def generic_caller(self, *args):
            _set_selftype(_mth_classtype[method])
            self = selftype.cast(self)
            args = _apply_types_to_fargs(argtypes, args)
            _set_selftype(None)
            return method(self, *args)

        generic_caller = EUDTypedFuncN(
            argn + 1, generic_caller, method, argtypes, rettypes, traced=traced
        )

        # Return function
        def call(self, *args):
            # Use purely eudfun method
            if isinstance(self, EUDStruct) or ev.IsEUDVariable(self):
                selftype = type(self)
                if method not in _mth_classtype:
                    _mth_classtype[method] = selftype

                _set_selftype(selftype)
                rets = generic_caller(self, *args)  # FIXME: euddraft#34
                _set_selftype(None)
                return rets

            # Const expression. Can use optimizations
            else:
                if self not in constexpr_callmap:

                    def caller(*args):
                        args = _apply_types_to_fargs(argtypes, args)
                        return method(self, *args)

                    constexpr_callmap[self] = EUDTypedFuncN(
                        argn, caller, method, argtypes, rettypes, traced=traced
                    )

                _set_selftype(type(self))
                rets = constexpr_callmap[self](*args)
                _set_selftype(None)
                return rets

        functools.update_wrapper(call, method)
        return call

    return _eud_typed_method


def EUDTracedTypedMethod(argtypes, rettypes=None):  # noqa: N802
    return EUDTypedMethod(argtypes, rettypes, traced=True)


def EUDMethod(method):  # noqa: N802
    return EUDTypedMethod(None, None, traced=False)(method)


def EUDTracedMethod(method):  # noqa: N802
    return EUDTypedMethod(None, None, traced=True)(method)
