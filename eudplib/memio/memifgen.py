#!/usr/bin/python
# Copyright 2018 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
from collections.abc import Callable

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from ..core.eudfunc.eudtypedfuncn import EUDTypedFuncN
from . import iotable
from . import modcurpl as cp


@functools.cache
def _read_epd_func(
    mask: int,
    initvals: tuple[int, ...],
    *args: tuple[int, ...],
    _check_empty: bool = False,
) -> EUDTypedFuncN:
    @_EUDPredefineReturn(len(args))
    @_EUDPredefineParam(cp.CP)
    @c.EUDFunc
    def readerfunc(targetplayer):
        ret = readerfunc._frets
        done = c.Forward()

        if _check_empty:
            check = c.Forward()
            check << c.RawTrigger(
                conditions=c.Deaths(cp.CP, c.Exactly, 0, 0),
                actions=[retv.SetNumber(0) for retv in ret]
                + [c.SetNextPtr(check, done)],
            )
            init = c.NextTrigger()

        cs.DoActions(
            [retv.SetNumber(initval) for retv, initval in zip(ret, initvals)]
        )

        for nth, i in enumerate(ut.bits(mask)):
            if all(arg[nth] == 0 for arg in args):
                continue
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, i),
                actions=[
                    retv.AddNumber(arg[nth])
                    for retv, arg in zip(ret, args)
                    if arg[nth] != 0
                ],
            )

        done << c.NextTrigger()
        cp.f_setcurpl2cpcache(
            actions=c.SetNextPtr(check, init) if _check_empty else []
        )
        # return ut.List2Assignable(ret)

    return readerfunc


def f_readgen_epd(
    mask: int,
    *args: tuple[int, Callable[[int], int]],
    docstring: str | None = None,
    _check_empty: bool = False,
) -> EUDTypedFuncN:
    mask = mask & 0xFFFFFFFF
    initvals = tuple(arg[0] for arg in args)
    vals = tuple(tuple(arg[1](i) for i in ut.bits(mask)) for arg in args)

    readerfunc = _read_epd_func(mask, initvals, *vals, _check_empty=_check_empty)
    if docstring:
        readerfunc.__doc__ = docstring
    return readerfunc


@functools.cache
def _read_cp_func(
    mask: int,
    initvals: tuple[int, ...],
    *args: tuple[int, ...],
    _check_empty: bool = False,
) -> Callable:
    @_EUDPredefineReturn(len(args))
    @c.EUDFunc
    def reader():
        ret = reader._frets
        init_actions = [
            retv.SetNumber(initval) for retv, initval in zip(ret, initvals)
        ]
        if _check_empty:
            check, read_start = c.Forward(), c.Forward()
            init_actions.append(c.SetNextPtr(check, read_start))
        cs.DoActions(init_actions)

        if _check_empty:
            done = c.Forward()
            check << c.RawTrigger(
                conditions=c.Deaths(cp.CP, c.Exactly, 0, 0),
                actions=[
                    retv.SetNumber(0)
                    for retv, initval in zip(ret, initvals)
                    if initval != 0
                ]
                + [c.SetNextPtr(check, done)],
            )
            read_start << c.NextTrigger()

        for nth, i in enumerate(ut.bits(mask)):
            if all(arg[nth] == 0 for arg in args):
                continue
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, i),
                actions=[
                    retv.AddNumber(arg[nth])
                    for retv, arg in zip(ret, args)
                    if arg[nth] != 0
                ],
            )

        if _check_empty:
            done << c.NextTrigger()
        # return ut.List2Assignable(ret)

    def readerfunc(cpo, **kwargs):
        if not isinstance(cpo, int) or cpo != 0:
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
        ret = [reader(**kwargs)]
        if not isinstance(cpo, int) or cpo != 0:
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
        return ut.List2Assignable(ret)

    return readerfunc


def f_readgen_cp(
    mask: int,
    *args: tuple[int, Callable[[int], int]],
    docstring: str | None = None,
    _check_empty: bool = False,
) -> Callable:
    mask = mask & 0xFFFFFFFF
    initvals = tuple(arg[0] for arg in args)
    vals = tuple(tuple(arg[1](i) for i in ut.bits(mask)) for arg in args)

    readerfunc = _read_cp_func(mask, initvals, *vals, _check_empty=_check_empty)
    if docstring:
        readerfunc.__doc__ = docstring
    return readerfunc


def f_maskread_epd(targetplayer, mask, *, _fdict={}, **kwargs):
    if iotable._is_consecutive(mask):
        return iotable._insert_or_get(mask, 0)(targetplayer, **kwargs)

    if mask not in _fdict:
        _fdict[mask] = f_readgen_epd(mask, (0, lambda x: x))
    return _fdict[mask](targetplayer, **kwargs)


def f_maskread_cp(cpoffset, mask, *, _fdict={}, **kwargs):
    if mask not in _fdict:
        _fdict[mask] = f_readgen_cp(mask, (0, lambda x: x))
    return _fdict[mask](cpoffset, **kwargs)
