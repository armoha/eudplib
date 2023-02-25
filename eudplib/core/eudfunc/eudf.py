#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

import functools
import inspect

from ... import utils as ut
from ...localize import _
from ..rawtrigger import CurrentPlayer
from ..variable import EUDVariable
from ..variable.evcommon import _ev
from .eudtypedfuncn import EUDFullFuncN, EUDTypedFuncN, EUDXTypedFuncN, applyTypes


def EUDTypedFunc(argtypes, rettypes=None, *, traced=False):
    def _EUDTypedFunc(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(argspec[1] is None, _("No variadic arguments (*args) allowed for EUDFunc."))
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
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
        ut.ep_assert(argspec[1] is None, _("No variadic arguments (*args) allowed for EUDFunc."))
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = applyTypes(argtypes, args)
            return fdecl_func(*args)

        ret = EUDXTypedFuncN(argn, caller, fdecl_func, argtypes, rettypes, argmasks, traced=traced)
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _EUDXTypedFunc


def EUDFullFunc(arginitvals, argtypes, rettypes=None, *, traced=False):
    def _EUDFullFunc(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(
            argn >= len(arginitvals),
            _("Different number of variables({}) from initial values({})").format(
                argn, len(arginitvals)
            ),
        )
        ut.ep_assert(argspec[1] is None, _("No variadic arguments (*args) allowed for EUDFunc."))
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = applyTypes(argtypes, args)
            return fdecl_func(*args)

        ret = EUDFullFuncN(
            argn, arginitvals, caller, fdecl_func, argtypes, rettypes, traced=traced
        )
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _EUDFullFunc


def _EUDPredefineParam(*args):
    """
    Use with cautions!
    1. Don't initialize value!
    2. Reset modifier to `SetTo` when you're done!
    3. Always SetDest when assign to other variables!
    4. No EUDFunc call in function body!
    """
    fnargs, slicer = list(), list()
    for arg in args:
        if arg is CurrentPlayer:
            fnargs.append(ut.EPD(0x6509B0))
        elif isinstance(arg, (list, tuple)):
            fnargs.extend(arg)
        else:
            slicer.append(arg)
    while slicer:
        try:
            arg = ut.FlattenList(_ev[slice(*slicer)])
            if arg:
                fnargs.extend(arg)
                break
        except IndexError:
            _ev.append(EUDVariable())
        else:
            _ev.append(EUDVariable())

    def wrapper(f):
        f._fargs = fnargs
        f._argn = len(fnargs)
        return f

    return wrapper


def _EUDPredefineReturn(*frets):
    """
    Use with cautions!
    1. Always initialize value!
    2. Reset modifier to `SetTo` when you're done!
    3. Don't modify Dest in function body!
    4. No EUDFunc call in function body!
    """
    while frets:
        try:
            ret = ut.FlattenList(_ev[slice(*frets)])
            if ret:
                frets = ret
                break
        except IndexError:
            _ev.append(EUDVariable())
        else:
            _ev.append(EUDVariable())

    def wrapper(f):
        f._frets = frets
        f._retn = len(frets)
        return f

    return wrapper
