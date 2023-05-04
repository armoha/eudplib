#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ... import utils as ut
from ...localize import _
from .. import allocator as ac
from .. import rawtrigger as rt
from ..eudstruct import EUDStruct, EUDVArray
from ..rawtrigger.rawtriggerdef import _DoActions
from ..variable import EUDVariable, SetVariables, VProc
from .eudfuncn import EUDFuncN
from .eudtypedfuncn import applyTypes

#
# Common argument / returns storage
#


def getArgStorage(argn, _argstorage_dict={}):
    """Get common arguments storage for argn"""
    if argn not in _argstorage_dict:
        _argstorage_dict[argn] = [EUDVariable() for _ in range(argn)]
    return _argstorage_dict[argn]


def getRetStorage(retn, _retstorage_dict={}):
    """Get common returns storage for retn"""
    if retn not in _retstorage_dict:
        _retstorage_dict[retn] = [EUDVariable() for _ in range(retn)]
    return _retstorage_dict[retn]


def fillArgumentsAndReturns(f):
    """Copy values from common argument storage to f._args,
    and queue assign from f_rets to common returns storage"""
    var = []
    actions = []
    if f._argn:
        argStorage = getArgStorage(f._argn)
        for farg, arg in zip(f._fargs, argStorage):
            var.append(arg)
            actions.append(arg.QueueAssignTo(farg))
    if f._retn:
        retStorage = getRetStorage(f._retn)
        for fret, ret in zip(f._frets, retStorage):
            actions.append(fret.SetDest(ret))
    if var:
        VProc(var, actions)
    elif actions:
        _DoActions(actions)


def callFuncBody(fstart, fend):
    """Call function's body triggers"""
    fcallend = ac.Forward()

    rt.RawTrigger(nextptr=fstart, actions=[rt.SetNextPtr(fend, fcallend)])

    fcallend << rt.NextTrigger()


def createIndirectCaller(f, _caller_dict={}):
    """Create function caller using common argument/return storage"""

    # Cache function in _caller_dict. If uncached,
    if f not in _caller_dict:
        rt.PushTriggerScope()
        caller_start = rt.NextTrigger()
        fillArgumentsAndReturns(f)
        callFuncBody(f._fstart, f._fend)
        caller_end = rt.RawTrigger()
        rt.PopTriggerScope()

        _caller_dict[f] = (caller_start, caller_end)

    return _caller_dict[f]


# ---------------------------------


def EUDTypedFuncPtr(argtypes, rettypes):
    argn = len(argtypes)
    retn = len(rettypes)

    class PtrDataClass(EUDStruct):
        _fields_ = ["_fstart", "_fendnext_epd"]

        def __init__(self, _from=None):
            if _from is not None and isinstance(_from, EUDFuncN):
                # Statically generate with EUDFuncN
                self.checkValidFunction(_from)
                f_idcstart, f_idcend = createIndirectCaller(_from)
                super().__init__(_from=EUDVArray(2)([f_idcstart, ut.EPD(f_idcend + 4)]))
            else:
                # Cast from EUDVariable or ConstExpr
                super().__init__(_from=_from)

        @classmethod
        def cast(cls, _from):
            return cls(_from=_from)

        def checkValidFunction(self, f):
            ut.ep_assert(isinstance(f, EUDFuncN), _("{} is not an EUDFuncN").format(f))
            if not f._fstart:
                f._CreateFuncBody()

            f_argn = f._argn
            f_retn = f._retn
            ut.ep_assert(
                argn == f_argn,
                _("Function requires {} arguments (Expected {})").format(f_argn, argn),
            )
            ut.ep_assert(
                retn == f_retn,
                _("Function returns {} values (Expected {})").format(f_retn, retn),
            )

        def setFunc(self, f):
            """Set function pointer's target to function

            :param f: Target function
            """
            try:
                self._fstart, self._fendnext_epd = f._fstart, f._fendnext_epd

            except AttributeError:
                self.checkValidFunction(f)

                # Build actions
                f_idcstart, f_idcend = createIndirectCaller(f)
                self._fstart = f_idcstart
                self._fendnext_epd = ut.EPD(f_idcend + 4)

        def __lshift__(self, rhs):
            self.setFunc(rhs)

        def __call__(self, *args):
            """Call target function with given arguments"""

            args = applyTypes(argtypes, args)

            if argn:
                argStorage = getArgStorage(argn)
                SetVariables(argStorage, args)

            # Call function
            t, a = ac.Forward(), ac.Forward()
            SetVariables([ut.EPD(t + 4), ut.EPD(a + 16)], [self._fstart, self._fendnext_epd])

            fcallend = ac.Forward()
            t << rt.RawTrigger(actions=[a << rt.SetNextPtr(0, fcallend)])
            fcallend << rt.NextTrigger()

            if retn:
                tmpRets = [EUDVariable() for _ in range(retn)]
                retStorage = getRetStorage(retn)
                SetVariables(tmpRets, retStorage)
                tmpRets = applyTypes(rettypes, tmpRets)
                return ut.List2Assignable(tmpRets)

    return PtrDataClass


def EUDFuncPtr(argn, retn):
    return EUDTypedFuncPtr([None] * argn, [None] * retn)
