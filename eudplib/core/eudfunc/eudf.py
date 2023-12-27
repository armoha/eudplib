#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
import inspect

from ... import utils as ut
from ...localize import _
from ..rawtrigger import CurrentPlayer
from ..variable import EUDVariable, IsEUDVariable
from ..variable.evcommon import _ev
from .eudtypedfuncn import EUDFullFuncN, EUDTypedFuncN, EUDXTypedFuncN, _apply_types


def EUDTypedFunc(argtypes, rettypes=None, *, traced=False):  # noqa: N802
    def _eud_typed_func(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(
            argspec[1] is None,
            _("No variadic arguments (*args) allowed for EUDFunc."),
        )
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = _apply_types(argtypes, args)
            return fdecl_func(*args)

        ret = EUDTypedFuncN(
            argn, caller, fdecl_func, argtypes, rettypes, traced=traced
        )
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _eud_typed_func


def EUDTracedTypedFunc(argtypes, rettypes=None):  # noqa: N802
    return EUDTypedFunc(argtypes, rettypes, traced=True)


def EUDFunc(fdecl_func):  # noqa: N802
    return EUDTypedFunc(None, None, traced=False)(fdecl_func)


def EUDTracedFunc(fdecl_func):  # noqa: N802
    return EUDTypedFunc(None, None, traced=True)(fdecl_func)


def EUDXTypedFunc(argmasks, argtypes, rettypes=None, *, traced=False):  # noqa: N802
    def _eudx_typed_func(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(
            argspec[1] is None,
            _("No variadic arguments (*args) allowed for EUDFunc."),
        )
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = _apply_types(argtypes, args)
            return fdecl_func(*args)

        ret = EUDXTypedFuncN(
            argn, caller, fdecl_func, argtypes, rettypes, argmasks, traced=traced
        )
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _eudx_typed_func


def EUDFullFunc(arginitvals, argtypes, rettypes=None, *, traced=False):  # noqa: N802
    def _eud_full_func(fdecl_func):
        argspec = inspect.getfullargspec(fdecl_func)
        argn = len(argspec[0])
        ut.ep_assert(
            argn >= len(arginitvals),
            _("Different number of variables({}) from initial values({})").format(
                argn, len(arginitvals)
            ),
        )
        ut.ep_assert(
            argspec[1] is None,
            _("No variadic arguments (*args) allowed for EUDFunc."),
        )
        ut.ep_assert(
            argspec[2] is None,
            _("No variadic keyword arguments (**kwargs) allowed for EUDFunc."),
        )

        def caller(*args):
            # Cast arguments to argtypes before callee code.
            args = _apply_types(argtypes, args)
            return fdecl_func(*args)

        ret = EUDFullFuncN(
            argn, arginitvals, caller, fdecl_func, argtypes, rettypes, traced=traced
        )
        functools.update_wrapper(ret, fdecl_func)
        return ret

    return _eud_full_func


def _EUDPredefineParam(*args):  # noqa: N802
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


def _EUDPredefineReturn(*frets):  # noqa: N802
    """
    Use with cautions!
    1. Always initialize value!
    2. Reset modifier to `SetTo` when you're done!
    3. Don't modify Dest in function body!
    4. No EUDFunc call in function body!
    """
    ut.ep_assert(frets)
    if len(frets) <= 2 and all(isinstance(ret, int) for ret in frets):
        while len(_ev) < max(frets):
            _ev.append(EUDVariable())
        rets = _ev[slice(*frets)]

    elif all(IsEUDVariable(ret) for ret in frets):
        rets = frets

    else:
        raise ut.EPError(_("Invalid return variable: {}").format(frets))

    rets = ut.FlattenList(rets)

    def wrapper(f):
        f._frets = rets
        f._retn = len(rets)
        return f

    return wrapper
