#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections.abc import Callable
import math
from eudplib import utils as ut

from .. import allocator as ac
from .. import eudfunc as ef
from .. import rawtrigger as rt
from .. import variable as ev
from ..variable.evcommon import _ev
from ...localize import _
from ..eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn


def f_mul(a, b, **kwargs):
    """Calculate a * b"""
    if ev.IsEUDVariable(a) and ev.IsEUDVariable(b):
        return _eud_mul(a, b, **kwargs)

    elif ev.IsEUDVariable(a):
        return _const_mul(b)(a, **kwargs)

    elif ev.IsEUDVariable(b):
        return _const_mul(a)(b, **kwargs)

    try:
        ret = kwargs["ret"][0]
    except KeyError:
        ret = ev.EUDVariable()
    ret << a * b
    return ret


def f_div(a, b, **kwargs):
    """Calculates quotient and remainder of a by b, with unsigned division.

    For signed division, uses `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."""
    if ut.isUnproxyInstance(a, int) and a < 0:
        raise ut.EPError(
            _("Can't use negative dividend for unsigned division: {}").format(a),
            _("For signed division, use `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."),
        )
    if ut.isUnproxyInstance(b, int) and b < 0:
        raise ut.EPError(
            _("Can't use negative divider for unsigned division: {}").format(a),
            _("For signed division, use `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."),
        )

    if ev.IsEUDVariable(b):
        return _eud_div(a, b, **kwargs)

    elif ev.IsEUDVariable(a):
        return _const_div(b)(a, **kwargs)

    if b:
        q, m = divmod(a, b)
    else:
        q, m = 0xFFFFFFFF, a
    try:
        vq, vm = kwargs["ret"]
    except KeyError:
        vq, vm = ev.EUDCreateVariables(2)
    ev.SeqCompute([(vq, rt.SetTo, q), (vm, rt.SetTo, m)])
    return vq, vm


def _quot(a, b, **kwargs):
    """Calculate (a//b)"""
    if ut.isUnproxyInstance(a, int) and a < 0:
        raise ut.EPError(
            _("Can't use negative dividend for unsigned division: {}").format(a),
            _("For signed division, use `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."),
        )
    if ut.isUnproxyInstance(b, int) and b < 0:
        raise ut.EPError(
            _("Can't use negative divider for unsigned division: {}").format(a),
            _("For signed division, use `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."),
        )

    if isinstance(b, ev.EUDVariable):
        return _eud_quot(a, b, **kwargs)

    elif isinstance(a, ev.EUDVariable):
        return _const_quot(b)(a, **kwargs)

    if b:
        q = a // b
    else:
        q = 0xFFFFFFFF, a
    try:
        vq = kwargs["ret"][0]
    except KeyError:
        vq = ev.EUDVariable()
    ev.SeqCompute([(vq, rt.SetTo, q)])
    return vq


def _rem(a, b, **kwargs):
    """Calculate (a%b)"""
    if ut.isUnproxyInstance(a, int) and a < 0:
        raise ut.EPError(
            _("Can't use negative dividend for unsigned division: {}").format(a),
            _("For signed division, use `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."),
        )
    if ut.isUnproxyInstance(b, int) and b < 0:
        raise ut.EPError(
            _("Can't use negative divider for unsigned division: {}").format(a),
            _("For signed division, use `f_div_towards_zero`, `f_div_floor` and `f_div_euclid`."),
        )

    if isinstance(b, ev.EUDVariable):
        return _eud_rem(a, b, **kwargs)

    elif isinstance(a, ev.EUDVariable):
        return _const_rem(b)(a, **kwargs)

    if b:
        m = a % b
    else:
        m = a
    try:
        vm = kwargs["ret"][0]
    except KeyError:
        vm = ev.EUDVariable()
    ev.SeqCompute([(vm, rt.SetTo, m)])
    return vm


# -------


def _const_mul(number: int) -> Callable:
    """
    f_constnum(a)(b) calculates b * a.

    :param number: Constant integer being multiplied to other numbers.
    :return: Function taking one parameter.
    """
    number &= 0xFFFFFFFF
    if not hasattr(_const_mul, "mulfdict"):
        from .bitwise import f_bitlshift

        @ef.EUDFunc
        def _mul_1(x):
            return -x

        @ef.EUDFunc
        def _mul0(x):
            return 0

        @ef.EUDFunc
        def _mul1(x):
            return x

        def _mul_pow2(p):
            def pow2(x, **kwargs):
                return f_bitlshift(x, p, **kwargs)

            return pow2

        setattr(
            _const_mul,
            "mulfdict",
            {
                0xFFFFFFFF: _mul_1,
                0: _mul0,
                1: _mul1,
                2**1: _mul_pow2(1),
                2**2: _mul_pow2(2),
                2**3: _mul_pow2(3),
                2**4: _mul_pow2(4),
                2**5: _mul_pow2(5),
                2**6: _mul_pow2(6),
                2**7: _mul_pow2(7),
            },
        )

    mulfdict = getattr(_const_mul, "mulfdict")

    try:
        return mulfdict[number]
    except KeyError:

        @_EUDPredefineParam(1)
        @_EUDPredefineReturn(1, 2)
        @ef.EUDFunc
        def _mulf(a):
            ret = _mulf._frets[0]
            ret << 0
            for i in ut.RandList(range(32)):
                if (2**i * number) & 0xFFFFFFFF == 0:
                    continue
                rt.RawTrigger(
                    conditions=a.AtLeastX(1, 2**i),
                    actions=ret.AddNumber(2**i * number),
                )
            # return ret

        mulfdict[number] = _mulf
        return _mulf


def _const_div(number: int) -> Callable:
    """
    _const_div(a)(b) calculates (b // a, b % a)

    :param number: Constant positive integer to divide other numbers by.
    :return: Function taking one parameter.
    """
    if not hasattr(_const_div, "divfdict"):

        @ef.EUDFunc
        def _div0(x):
            return -1, x

        @ef.EUDFunc
        def _div1(x):
            return x, 0

        setattr(_const_div, "divfdict", {0: _div0, 1: _div1})

    divfdict = getattr(_const_div, "divfdict")

    try:
        return divfdict[number]
    except KeyError:

        @_EUDPredefineReturn(2)
        @_EUDPredefineParam(1, 2)
        @ef.EUDFunc
        def _divf(a):
            quotient = _divf._frets[0]
            quotient << 0
            for i in range(31, -1, -1):
                # number too big
                if 2**i * number >= 2**32:
                    continue

                if number & (number - 1) == 0:
                    rt.RawTrigger(
                        conditions=a.AtLeastX(1, 2**i * number),
                        actions=quotient.AddNumber(2**i),
                    )
                else:
                    rt.RawTrigger(
                        conditions=a.AtLeast(2**i * number),
                        actions=[
                            a.SubtractNumber(2**i * number),
                            quotient.AddNumber(2**i),
                        ],
                    )
            if number & (number - 1) == 0:
                a &= number - 1
            # return quotient, a

        divfdict[number] = _divf
        return _divf


def _const_quot(number: int) -> Callable:
    """
    _const_quot(a)(b) calculates (b // a)

    :param number: Constant positive integer to divide other numbers by.
    :return: Function taking one parameter.
    """
    if not hasattr(_const_quot, "quotfdict"):

        @ef.EUDFunc
        def _quot0(x):
            return -1

        @ef.EUDFunc
        def _quot1(x):
            return x

        setattr(_const_quot, "quotfdict", {0: _quot0, 1: _quot1})

    quotfdict = getattr(_const_quot, "quotfdict")

    try:
        return quotfdict[number]
    except KeyError:

        if number & (number - 1) == 0:  # a // powOf2 = a >> log2(powOf2)

            @_EUDPredefineReturn(1)
            @_EUDPredefineParam(1)
            @ef.EUDFunc
            def _quotf(quotient):
                ev.vbase.VariableBase.__irshift__(quotient, int(math.log2(number)))
                # return quotient

        else:

            @_EUDPredefineReturn(1)
            @ef.EUDFunc
            def _quotf(a):
                quotient = _quotf._frets[0]
                quotient << 0
                for i in range(31, -1, -1):
                    # number too big
                    if 2**i * number >= 2**32:
                        continue

                    rt.RawTrigger(
                        conditions=a.AtLeast(2**i * number),
                        actions=[
                            a.SubtractNumber(2**i * number),
                            quotient.AddNumber(2**i),
                        ],
                    )
                # return quotient

        quotfdict[number] = _quotf
        return _quotf


def _const_rem(number: int) -> Callable:
    """
    _const_rem(a)(b) calculates (b // a)

    :param number: Constant positive integer to divide other numbers by.
    :return: Function taking one parameter.
    """
    if not hasattr(_const_rem, "remfdict"):

        @ef.EUDFunc
        def _rem0(x):
            return x

        @ef.EUDFunc
        def _rem1(x):
            return 0

        setattr(_const_rem, "remfdict", {0: _rem0, 1: _rem1})

    remfdict = getattr(_const_rem, "remfdict")

    try:
        return remfdict[number]
    except KeyError:

        if number & (number - 1) == 0:

            @_EUDPredefineReturn(1)
            @_EUDPredefineParam(1)
            @ef.EUDFunc
            def _remf(remainder):
                remainder &= number - 1
                # return remainder

        else:

            @_EUDPredefineReturn(1)
            @_EUDPredefineParam(1)
            @ef.EUDFunc
            def _remf(a):
                for i in range(31, -1, -1):
                    # number too big
                    if 2**i * number >= 2**32:
                        continue

                    rt.RawTrigger(
                        conditions=a.AtLeast(2**i * number),
                        actions=a.SubtractNumber(2**i * number),
                    )
                # return remainder

        remfdict[number] = _remf
        return _remf


# -------


@_EUDPredefineReturn(1)
@ef.EUDFunc
def _eud_mul(a, b):
    ret = _eud_mul._frets[0]
    endmul, reset_nptr = ac.Forward(), ac.Forward()

    # Init
    rt.RawTrigger(actions=[ret.SetNumber(0), b.SetModifier(rt.Add)])
    remaining_bits = 0xFFFFFFFF

    # Run multiplication chain
    for i in range(32):
        remaining_bits -= 1 << i
        p1, p2, p3, p4 = [ac.Forward() for _ in range(4)]
        p1 << rt.RawTrigger(
            nextptr=p2,
            conditions=a.AtLeastX(1, 2**i),
            actions=rt.SetNextPtr(p1, p3),
        )
        p3 << ev.VProc(b, [b.SetDest(ret), rt.SetNextPtr(p1, p2)])
        p2 << rt.NextTrigger()
        if i <= 30:
            acts = [
                rt.SetNextPtr(p2, endmul),
                rt.SetMemory(reset_nptr + 16, rt.SetTo, ut.EPD(p2 + 4)),
                rt.SetMemory(reset_nptr + 20, rt.SetTo, p4),
            ]
            rt.RawTrigger(
                nextptr=p4,
                conditions=a.ExactlyX(0, remaining_bits),
                actions=ut.RandList(acts),
            )
            p4 << ev.VProc(b, b.SetDest(b))  # b += b

    endmul << rt.RawTrigger(actions=[reset_nptr << rt.SetNextPtr(p1, p2)])
    # return ret


@ef.EUDFunc
def _eud_div(a, b):
    ret, x = ev.EUDCreateVariables(2)

    # Init
    ev.SeqCompute([(ret, rt.SetTo, 0), (x, rt.SetTo, b)])

    # Chain ac.Forward decl
    chain_x0 = [ac.Forward() for _ in range(32)]
    chain_x1 = [ac.Forward() for _ in range(32)]
    chain = [ac.Forward() for _ in range(32)]

    # Fill in chain
    for i in range(32):
        ev.SeqCompute([(ut.EPD(chain_x0[i]), rt.SetTo, x), (ut.EPD(chain_x1[i]), rt.SetTo, x)])

        # Skip if over 0x80000000
        p1, p2, p3 = ac.Forward(), ac.Forward(), ac.Forward()
        p1 << rt.RawTrigger(
            nextptr=p2,
            conditions=x.AtLeastX(1, 0x80000000),
            actions=rt.SetNextPtr(p1, p3),
        )
        p3 << rt.RawTrigger(nextptr=chain[i], actions=rt.SetNextPtr(p1, p2))
        p2 << rt.NextTrigger()

        ev.SeqCompute([(x, rt.Add, x)])

    # Run division chain
    for i in range(31, -1, -1):
        cx0, cx1 = ac.Forward(), ac.Forward()
        chain[i] << rt.RawTrigger(
            conditions=[cx0 << a.AtLeast(0)],
            actions=[cx1 << a.SubtractNumber(0), ret.AddNumber(2**i)],
        )

        chain_x0[i] << cx0 + 8
        chain_x1[i] << cx1 + 20

    return ret, a  # a : remainder


def _eud_quot(a, b, **kwargs):
    ret = kwargs.get("ret")
    if ret is not None:
        ret.append(_ev[4])
    quot = _eud_div(a, b, **kwargs)[0]
    return ret[0] if ret else quot


def _eud_rem(a, b, **kwargs):
    ret = kwargs.get("ret")
    if ret is not None:
        ret.insert(0, _ev[4])
    rem = _eud_div(a, b, **kwargs)[1]
    return ret[1] if ret else rem
