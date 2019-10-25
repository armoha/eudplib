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

from ... import utils as ut
from .. import variable as ev

from .eudfuncn import EUDFuncN


def applyTypes(typesdecl, varlist):
    """
    EUD-Typecast each variable to declared types.

    :param typesdecl: List of types. Can be set to None if you don't want
        to typecast anything. Each item of the list can also be None which is
        equivilant to EUDVariable here.
    :param varlist: List of variables.

    :returns: List of casted variables.
    """
    if typesdecl is None:
        return varlist

    ut.ep_assert(
        len(varlist) == len(typesdecl),
        "Different number of variables(%d) from type declarations(%d)"
        % (len(varlist), len(typesdecl)),
    )

    rets = []
    for vartype, var in zip(typesdecl, varlist):
        if vartype == ev.EUDVariable or vartype is None:
            rets.append(var)
        else:
            rets.append(vartype.cast(var))

    return rets


class EUDTypedFuncN(EUDFuncN):

    """
    EUDFuncN specialization for EUDTypedFunc. This will pre-convert
    arguments to types prior to function call.
    """

    def __init__(self, argn, callerfunc, bodyfunc, argtypes, rettypes, *, traced):
        super().__init__(argn, callerfunc, bodyfunc, traced=traced)
        self._argtypes = argtypes
        self._rettypes = rettypes

    def __call__(self, *args, ret=None):
        # This layer is nessecary for function to accept non-EUDVariable object
        # as argument. For instance, EUDFuncN.
        args = applyTypes(self._argtypes, args)
        rets = super().__call__(*args, ret=ret)

        # Cast returns to rettypes before caller code.
        rets = ut.Assignable2List(rets)
        rets = applyTypes(self._rettypes, rets)
        return ut.List2Assignable(rets)


class EUDXTypedFuncN(EUDTypedFuncN):

    """
    EUDFuncN specialization for EUDX.
    """

    def __init__(
        self, argn, callerfunc, bodyfunc, argtypes, rettypes, argmasks, *, traced
    ):
        super().__init__(argn, callerfunc, bodyfunc, argtypes, rettypes, traced=traced)
        self._argmasks = argmasks

    def _CreateFuncArgs(self):
        ut.ep_assert(
            self._argn == len(self._argmasks),
            "Number of argument masks should be constant",
        )
        self._fargs = [ev.EUDXVariable(0, mask) for mask in self._argmasks]
