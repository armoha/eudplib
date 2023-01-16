#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ... import utils as ut
from ...localize import _
from .. import rawtrigger as bt
from .. import variable as ev
from .eudfuncn import EUDFuncN


def applyTypes(typesdecl, varlist):
    """
    EUD-Typecast each variable to declared types.

    :param typesdecl: List of types. Can be set to None if you don't want
        to typecast anything. Each item of the list can also be None which is
        equivalent to EUDVariable here.
    :param varlist: List of variables.

    :returns: List of casted variables.
    """
    if typesdecl is None:
        return varlist

    rets = []
    # FIXME: armoha/euddraft#34
    if len(varlist) == len(typesdecl) + 1:
        rets.append(varlist[0])
        varlist = varlist[1:]
    ut.ep_assert(
        len(varlist) == len(typesdecl),
        _("Different number of variables({}) from type declarations({})").format(
            len(varlist), len(typesdecl)
        )
        + f"argtypes: {typesdecl}, args: {varlist}",
    )

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
        # This layer is necessary for function to accept non-EUDVariable object
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

    def __init__(self, argn, callerfunc, bodyfunc, argtypes, rettypes, argmasks, *, traced):
        super().__init__(argn, callerfunc, bodyfunc, argtypes, rettypes, traced=traced)
        self._argmasks = argmasks

    def _CreateFuncArgs(self):
        ut.ep_assert(
            self._argn == len(self._argmasks),
            _("Different number of arguments({}) from mask declarations({})."),
        )
        if self._fargs is None:
            self._fargs = [ev.EUDXVariable(0, mask) for mask in self._argmasks]


class EUDFullFuncN(EUDFuncN):
    def __init__(self, argn, arginitvals, callerfunc, bodyfunc, argtypes, rettypes, *, traced):
        arginitvals = list(arginitvals)
        while len(arginitvals) < argn:
            arginitvals.append((0, bt.SetTo, 0, None))
        super().__init__(arginitvals, callerfunc, bodyfunc, traced=traced)
        self._argtypes = argtypes
        self._rettypes = rettypes

    def __call__(self, *args, ret=None):
        # This layer is necessary for function to accept non-EUDVariable object
        # as argument. For instance, EUDFuncN.
        args = applyTypes(self._argtypes, args)
        rets = super().__call__(*args, ret=ret)

        # Cast returns to rettypes before caller code.
        rets = ut.Assignable2List(rets)
        rets = applyTypes(self._rettypes, rets)
        return ut.List2Assignable(rets)
