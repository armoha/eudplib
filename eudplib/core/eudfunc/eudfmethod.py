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
from ..eudstruct.selftype import SetSelfType, selftype
from .eudtypedfuncn import EUDTypedFuncN, applyTypes

_mth_classtype: dict[Callable, type] = {}


def EUDTypedMethod(argtypes, rettypes=None, *, traced=False):
    def _EUDTypedMethod(method):
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
        def genericCaller(self, *args):
            SetSelfType(_mth_classtype[method])
            self = selftype.cast(self)
            args = applyTypes(argtypes, args)
            SetSelfType(None)
            return method(self, *args)

        genericCaller = EUDTypedFuncN(
            argn + 1, genericCaller, method, argtypes, rettypes, traced=traced
        )

        # Return function
        def call(self, *args):
            # Use purely eudfun method
            if ev.IsEUDVariable(self):
                selftype = type(self)
                if method not in _mth_classtype:
                    _mth_classtype[method] = selftype

                SetSelfType(selftype)
                rets = genericCaller(self, *args)  # FIXME: euddraft#34
                SetSelfType(None)
                return rets

            # Const expression. Can use optimizations
            else:
                if self not in constexpr_callmap:

                    def caller(*args):
                        args = applyTypes(argtypes, args)
                        return method(self, *args)

                    constexpr_callmap[self] = EUDTypedFuncN(
                        argn, caller, method, argtypes, rettypes, traced=traced
                    )

                SetSelfType(type(self))
                rets = constexpr_callmap[self](*args)
                SetSelfType(None)
                return rets

        functools.update_wrapper(call, method)
        return call

    return _EUDTypedMethod


def EUDTracedTypedMethod(argtypes, rettypes=None):
    return EUDTypedMethod(argtypes, rettypes, traced=True)


def EUDMethod(method):
    return EUDTypedMethod(None, None, traced=False)(method)


def EUDTracedMethod(method):
    return EUDTypedMethod(None, None, traced=True)(method)
