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

from .. import allocator as ac, rawtrigger as rt, variable as ev, eudfunc as ef

from eudplib import utils as ut
from ..eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn


def f_mul(a, b, **kwargs):
    """Calculate a * b"""
    if isinstance(a, ev.EUDVariable) and isinstance(b, ev.EUDVariable):
        return _f_mul(a, b, **kwargs)

    elif isinstance(a, ev.EUDVariable):
        return f_constmul(b)(a, **kwargs)

    elif isinstance(b, ev.EUDVariable):
        return f_constmul(a)(b, **kwargs)

    try:
        ret = kwargs["ret"][0]
    except KeyError:
        ret = ev.EUDVariable()
    ret << a * b
    return ret


def f_div(a, b, **kwargs):
    """Calculate (a//b, a%b)"""
    if isinstance(b, ev.EUDVariable):
        return _f_div(a, b, **kwargs)

    elif isinstance(a, ev.EUDVariable):
        return f_constdiv(b)(a, **kwargs)

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


# -------


def f_constmul(number):
    """
    f_constnum(a)(b) calculates b * a.

    :param number: Constant integer being multiplied to other numbers.
    :return: Function taking one parameter.
    """
    number &= 0xFFFFFFFF
    if not hasattr(f_constmul, "mulfdict"):
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

        f_constmul.mulfdict = {
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
        }

    mulfdict = f_constmul.mulfdict

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
                rt.RawTrigger(
                    conditions=a.AtLeastX(1, 2**i),
                    actions=ret.AddNumber(2**i * number),
                )
            # return ret

        mulfdict[number] = _mulf
        return _mulf


def f_constdiv(number):
    """
    f_constdiv(a)(b) calculates (b // a, b % a)

    :param number: Constant integer to divide other numbers by.
    :return: Function taking one parameter.
    """
    if not hasattr(f_constdiv, "divfdict"):

        @ef.EUDFunc
        def _div0(x):
            return -1, x

        @ef.EUDFunc
        def _div1(x):
            return x, 0

        f_constdiv.divfdict = {0: _div0, 1: _div1}

    divfdict = f_constdiv.divfdict

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

                rt.RawTrigger(
                    conditions=a.AtLeast(2**i * number),
                    actions=[
                        a.SubtractNumber(2**i * number),
                        quotient.AddNumber(2**i),
                    ],
                )
            # return quotient, a

        divfdict[number] = _divf
        return _divf


# -------


@_EUDPredefineReturn(1)
@ef.EUDFunc
def _f_mul(a, b):
    ret = _f_mul._frets[0]
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
def _f_div(a, b):
    ret, x = ev.EUDCreateVariables(2)

    # Init
    ev.SeqCompute([(ret, rt.SetTo, 0), (x, rt.SetTo, b)])

    # Chain ac.Forward decl
    chain_x0 = [ac.Forward() for _ in range(32)]
    chain_x1 = [ac.Forward() for _ in range(32)]
    chain = [ac.Forward() for _ in range(32)]

    # Fill in chain
    for i in range(32):
        ev.SeqCompute(
            [(ut.EPD(chain_x0[i]), rt.SetTo, x), (ut.EPD(chain_x1[i]), rt.SetTo, x)]
        )

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
