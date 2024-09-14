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
from ..variable import EUDVariable, SetVariables, VProc
from .eudfuncn import EUDFuncN
from .eudtypedfuncn import _apply_types

#
# Common argument / returns storage
#


def _get_arg_storage(argn, _argstorage_dict={}):
    """Get common arguments storage for argn"""
    if argn not in _argstorage_dict:
        _argstorage_dict[argn] = [EUDVariable() for _ in range(argn)]
    return _argstorage_dict[argn]


def _get_ret_storage(retn, _retstorage_dict={}):
    """Get common returns storage for retn"""
    if retn not in _retstorage_dict:
        _retstorage_dict[retn] = [EUDVariable() for _ in range(retn)]
    return _retstorage_dict[retn]


def _fill_arguments(f):
    """Copy values from common argument storage to f._args"""
    if f._argn:
        arg_storage = _get_arg_storage(f._argn)
        for farg, arg in zip(f._fargs, arg_storage):
            VProc(arg, arg.QueueAssignTo(farg))


def _fill_returns(f):
    """Copy values from f_rets to common returns storage"""
    if f._retn:
        ret_storage = _get_ret_storage(f._retn)
        for fret, ret in zip(f._frets, ret_storage):
            VProc(fret, fret.QueueAssignTo(ret))


def _call_func_body(fstart, fend):
    """Call function's body triggers"""
    fcallend = ac.Forward()

    rt.RawTrigger(nextptr=fstart, actions=[rt.SetNextPtr(fend, fcallend)])

    fcallend << rt.NextTrigger()


def _create_indirect_caller(f, _caller_dict={}):
    """Create function caller using common argument/return storage"""

    # Cache function in _caller_dict. If uncached,
    if f not in _caller_dict:
        rt.PushTriggerScope()
        caller_start = rt.NextTrigger()
        _fill_arguments(f)
        _call_func_body(f._fstart, f._fend)
        _fill_returns(f)
        caller_end = rt.RawTrigger()
        rt.PopTriggerScope()

        _caller_dict[f] = (caller_start, caller_end)

    return _caller_dict[f]


# ---------------------------------


def EUDTypedFuncPtr(argtypes, rettypes):  # noqa: N802
    argn = len(argtypes)
    retn = len(rettypes)

    class PtrDataClass(EUDStruct):
        _fields_ = ("_fstart", "_fendnext_epd")

        def __init__(self, _from=None) -> None:
            if _from is not None and isinstance(_from, EUDFuncN):
                # Statically generate with EUDFuncN
                self._check_valid_function(_from)
                f_idcstart, f_idcend = _create_indirect_caller(_from)
                super().__init__(
                    _from=EUDVArray(2)([f_idcstart, ut.EPD(f_idcend + 4)])
                )
            else:
                # Cast from EUDVariable or ConstExpr
                super().__init__(_from=_from)

        @classmethod
        def cast(cls, _from):
            return cls(_from=_from)

        def _check_valid_function(self, f):
            ut.ep_assert(
                isinstance(f, EUDFuncN), _("{} is not an EUDFuncN").format(f)
            )
            if not f._fstart:
                f._create_func_body()

            f_argn = f._argn
            f_retn = f._retn
            ut.ep_assert(
                argn == f_argn,
                _("Function requires {} arguments (Expected {})").format(
                    f_argn, argn
                ),
            )
            ut.ep_assert(
                retn == f_retn,
                _("Function returns {} values (Expected {})").format(f_retn, retn),
            )

        def setFunc(self, f):  # noqa: N802
            """Set function pointer's target to function

            :param f: Target function
            """
            try:
                self._fstart, self._fendnext_epd = f._fstart, f._fendnext_epd

            except AttributeError:
                self._check_valid_function(f)

                # Build actions
                f_idcstart, f_idcend = _create_indirect_caller(f)
                self._fstart = f_idcstart
                self._fendnext_epd = ut.EPD(f_idcend + 4)

        def __lshift__(self, rhs):
            self.setFunc(rhs)

        def __call__(self, *args):
            """Call target function with given arguments"""

            args = _apply_types(argtypes, args)

            if argn:
                arg_storage = _get_arg_storage(argn)
                SetVariables(arg_storage, args)

            # Call function
            t, a = ac.Forward(), ac.Forward()
            SetVariables(
                [ut.EPD(t + 4), ut.EPD(a + 16)],
                [self._fstart, self._fendnext_epd],
            )

            fcallend = ac.Forward()
            t << rt.RawTrigger(actions=[a << rt.SetNextPtr(0, fcallend)])
            fcallend << rt.NextTrigger()

            if retn:
                tmp_rets = [EUDVariable() for _ in range(retn)]
                ret_storage = _get_ret_storage(retn)
                SetVariables(tmp_rets, ret_storage)
                tmp_rets = _apply_types(rettypes, tmp_rets)
                return ut.List2Assignable(tmp_rets)

    return PtrDataClass


def EUDFuncPtr(argn, retn):  # noqa: N802
    return EUDTypedFuncPtr([None] * argn, [None] * retn)
