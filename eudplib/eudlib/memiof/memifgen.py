#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2018 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from ... import core as c
from ... import ctrlstru as cs
from ... import utils as ut
from ...core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from . import modcurpl as cp


def f_readgen_epd(mask, *args, docstring=None, _fdict={}, _check_empty=False):
    mask = mask & 0xFFFFFFFF
    if mask not in _fdict:
        _fdict[mask] = dict()
    _subfdict = _fdict[mask]

    key = (
        tuple(initval for initval, _ in args)
        + tuple(tuple(func(i) for i in ut.bits(mask)) for _, func in args)
        + (_check_empty,)
    )
    if key not in _subfdict:

        @_EUDPredefineReturn(len(args))
        @_EUDPredefineParam(c.CurrentPlayer)
        @c.EUDFunc
        def f_read_epd_template(targetplayer):
            ret = f_read_epd_template._frets
            done = c.Forward()

            if _check_empty:
                check = c.Forward()
                check << c.RawTrigger(
                    conditions=c.Deaths(c.CurrentPlayer, c.Exactly, 0, 0),
                    actions=[retv.SetNumber(0) for retv in ret] + [c.SetNextPtr(check, done)],
                )
                init = c.NextTrigger()

            cs.DoActions([retv.SetNumber(arg[0]) for retv, arg in zip(ret, args)])

            for i in ut.bits(mask):
                if all(arg[1](i) == 0 for arg in args):
                    continue
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, i),
                    actions=[
                        retv.AddNumber(arg[1](i)) for retv, arg in zip(ret, args) if arg[1](i) != 0
                    ],
                )

            done << c.NextTrigger()
            cp.f_setcurpl2cpcache(actions=c.SetNextPtr(check, init) if _check_empty else [])
            # return ut.List2Assignable(ret)

        if docstring:
            f_read_epd_template.__doc__ = docstring
        _subfdict[key] = f_read_epd_template
    return _subfdict[key]


def f_readgen_cp(mask, *args, docstring=None, _fdict={}, _check_empty=False):
    mask = mask & 0xFFFFFFFF
    if mask not in _fdict:
        _fdict[mask] = dict()
    _subfdict = _fdict[mask]

    key = (
        tuple(initval for initval, _ in args)
        + tuple(tuple(func(i) for i in ut.bits(mask)) for _, func in args)
        + (_check_empty,)
    )
    if key not in _subfdict:

        @_EUDPredefineReturn(len(args))
        @c.EUDFunc
        def readerf():
            ret = readerf._frets
            init_actions = [retv.SetNumber(arg[0]) for retv, arg in zip(ret, args)]
            if _check_empty:
                check, read_start = c.Forward(), c.Forward()
                init_actions.append(c.SetNextPtr(check, read_start))
            cs.DoActions(init_actions)

            if _check_empty:
                done = c.Forward()
                check << c.RawTrigger(
                    conditions=c.Deaths(c.CurrentPlayer, c.Exactly, 0, 0),
                    actions=[retv.SetNumber(0) for retv, arg in zip(ret, args) if arg[0] != 0]
                    + [c.SetNextPtr(check, done)],
                )
                read_start << c.NextTrigger()

            for i in ut.bits(mask):
                if all(arg[1](i) == 0 for arg in args):
                    continue
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, i),
                    actions=[
                        retv.AddNumber(arg[1](i)) for retv, arg in zip(ret, args) if arg[1](i) != 0
                    ],
                )

            if _check_empty:
                done << c.NextTrigger()
            # return ut.List2Assignable(ret)

        def f_read_cp_template(cpo, **kwargs):
            if not isinstance(cpo, int) or cpo != 0:
                cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
            ret = [readerf(**kwargs)]
            if not isinstance(cpo, int) or cpo != 0:
                cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
            return ut.List2Assignable(ret)

        if docstring:
            f_read_cp_template.__doc__ = docstring
        _subfdict[key] = f_read_cp_template
    return _subfdict[key]


def _getMapSize():
    from ...core.mapdata import GetChkTokenized

    chkt = GetChkTokenized()
    dim = chkt.getsection("DIM")
    x, y = ut.b2i2(dim[0:2]), ut.b2i2(dim[2:4])
    x, y = (x - 1).bit_length(), (y - 1).bit_length()
    x = 2 ** (x + 5) - 1
    y = 2 ** (y + 5) - 1
    return x + y * 0x10000


f_cunitread_epd = f_readgen_epd(0x3FFFF0, (0x400008, lambda x: x), _check_empty=True)
f_cunitread_cp = f_readgen_cp(0x3FFFF0, (0x400008, lambda x: x), _check_empty=True)
f_cunitepdread_epd = f_readgen_epd(
    0x3FFFF0,
    (0x400008, lambda x: x),
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_cunitepdread_cp = f_readgen_cp(
    0x3FFFF0,
    (0x400008, lambda x: x),
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_epdcunitread_epd = f_readgen_epd(
    0x3FFFF0,
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_epdcunitread_cp = f_readgen_cp(
    0x3FFFF0,
    (0x100002 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_epdspriteread_epd = f_readgen_epd(
    0x1FFFC, (0x188000 - 0x58A364 // 4, lambda x: x // 4), _check_empty=True
)
f_epdspriteread_cp = f_readgen_cp(
    0x1FFFC, (0x188000 - 0x58A364 // 4, lambda x: x // 4), _check_empty=True
)
f_spriteepdread_epd = f_readgen_epd(
    0x1FFFC,
    (0x620000, lambda x: x),
    (0x188000 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_spriteepdread_cp = f_readgen_cp(
    0x1FFFC,
    (0x620000, lambda x: x),
    (0x188000 - 0x58A364 // 4, lambda y: y // 4),
    _check_empty=True,
)
f_spriteread_epd = f_readgen_epd(0x1FFFC, (0x620000, lambda x: x), _check_empty=True)
f_spriteread_cp = f_readgen_cp(0x1FFFC, (0x620000, lambda x: x), _check_empty=True)


def _posread_epd():
    f = getattr(_posread_epd, "f", None)
    if f is None:
        f = f_readgen_epd(
            _getMapSize(),
            (0, lambda x: x if x <= 0xFFFF else 0),
            (0, lambda y: y >> 16),
        )
        _posread_epd.f = f
    return f


def f_posread_epd(epd, **kwargs):
    return _posread_epd()(epd, **kwargs)


def f_posread_cp(cpoffset, **kwargs):
    _rf = getattr(f_posread_cp, "_rf", None)
    if _rf is None:
        _rf = f_readgen_cp(
            _getMapSize(),
            (0, lambda x: x if x <= 0xFFFF else 0),
            (0, lambda y: y >> 16),
        )
        f_posread_cp._rf = _rf
    return _rf(cpoffset, **kwargs)


def f_maskread_epd(targetplayer, mask, _fdict={}, **kwargs):
    if mask not in _fdict:
        _fdict[mask] = f_readgen_epd(mask, (0, lambda x: x))
    return _fdict[mask](targetplayer, **kwargs)


def f_maskread_cp(cpoffset, mask, _fdict={}, **kwargs):
    if mask not in _fdict:
        _fdict[mask] = f_readgen_cp(mask, (0, lambda x: x))
    return _fdict[mask](cpoffset, **kwargs)
