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

import inspect
import functools

from .eudtypedfuncn import EUDTypedFuncN, applyTypes, EUDXTypedFuncN
from ... import utils as ut


def EUDTypedFunc(argtypes, rettypes=None, *, traced=False):
    def _EUDTypedFunc(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(
            argspec[1] is None, "No variadic arguments (*args) allowed for EUDFunc."
        )
        ut.ep_assert(
            argspec[2] is None,
            "No variadic keyword arguments (*kwargs) allowed for EUDFunc.",
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = applyTypes(argtypes, args)
            return fdecl_func(*args)

        ret = EUDTypedFuncN(argn, caller, fdecl_func, argtypes, rettypes, traced=traced)
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _EUDTypedFunc


def EUDTracedTypedFunc(argtypes, rettypes=None):
    return EUDTypedFunc(argtypes, rettypes, traced=True)


def EUDFunc(fdecl_func):
    return EUDTypedFunc(None, None, traced=False)(fdecl_func)


def EUDTracedFunc(fdecl_func):
    return EUDTypedFunc(None, None, traced=True)(fdecl_func)


def EUDXTypedFunc(argmasks, argtypes, rettypes=None, *, traced=False):
    def _EUDXTypedFunc(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(
            argspec[1] is None, "No variadic arguments (*args) allowed for EUDFunc."
        )
        ut.ep_assert(
            argspec[2] is None,
            "No variadic keyword arguments (*kwargs) allowed for EUDFunc.",
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = applyTypes(argtypes, args)
            return fdecl_func(*args)

        ret = EUDXTypedFuncN(argn, caller, fdecl_func, argtypes, rettypes, argmasks, traced=traced)
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _EUDXTypedFunc
