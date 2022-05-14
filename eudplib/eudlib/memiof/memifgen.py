#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2018 Armoha

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

from . import modcurpl as cp
from ... import core as c, ctrlstru as cs, utils as ut
from ...core.eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn


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
            cs.DoActions([retv.SetNumber(arg[0]) for retv, arg in zip(ret, args)])

            if _check_empty and not all(arg[0] == 0 for arg in args):
                c.RawTrigger(
                    conditions=c.Deaths(c.CurrentPlayer, c.Exactly, 0, 0),
                    actions=[
                        retv.SetNumber(0) if arg[0] != 0 else []
                        for retv, arg in zip(ret, args)
                    ],
                )

            for i in ut.bits(mask):
                if all(arg[1](i) == 0 for arg in args):
                    continue
                c.RawTrigger(
                    conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, i),
                    actions=[
                        retv.AddNumber(arg[1](i)) if arg[1](i) != 0 else []
                        for retv, arg in zip(ret, args)
                    ],
                )

            cp.f_setcurpl2cpcache()
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
            cs.DoActions([retv.SetNumber(arg[0]) for retv, arg in zip(ret, args)])

            if _check_empty and not all(arg[0] == 0 for arg in args):
                c.RawTrigger(
                    conditions=c.Deaths(c.CurrentPlayer, c.Exactly, 0, 0),
                    actions=[
                        retv.SetNumber(0) if arg[0] != 0 else []
                        for retv, arg in zip(ret, args)
                    ],
                )

            for i in ut.bits(mask):
                if all(arg[1](i) == 0 for arg in args):
                    continue
                c.RawTrigger(
                    conditions=[c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, i)],
                    actions=[
                        retv.AddNumber(arg[1](i)) if arg[1](i) != 0 else []
                        for retv, arg in zip(ret, args)
                    ],
                )

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
f_spriteread_epd = lambda epd: f_spriteepdread_epd(epd)[0]
f_spriteread_cp = lambda cpoffset: f_spriteepdread_cp(cpoffset)[0]


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
