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

import functools
import inspect

from ... import utils as ut
from ...localize import _
from .. import variable as ev
from ..eudstruct.selftype import SetSelfType, selftype
from .eudtypedfuncn import EUDTypedFuncN, applyTypes

_mth_classtype = {}


def EUDTypedMethod(argtypes, rettypes=None, *, traced=False):
    def _EUDTypedMethod(method):
        # Get argument number of fdecl_func
        argspec = inspect.getfullargspec(method)
        ut.ep_assert(argspec[1] is None, _("No variadic arguments (*args) allowed for EUDFunc."))
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
                return genericCaller(self, *args)

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
