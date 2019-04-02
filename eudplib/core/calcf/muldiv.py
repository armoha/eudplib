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


def f_mul(a, b):
    """Calculate a * b"""
    if isinstance(a, ev.EUDVariable) and isinstance(b, ev.EUDVariable):
        return _f_mul(a, b)

    elif isinstance(a, ev.EUDVariable):
        return f_constmul(b)(a)

    elif isinstance(b, ev.EUDVariable):
        return f_constmul(a)(b)

    else:
        ret = ev.EUDVariable()
        ret << a * b
        return ret


def f_div(a, b):
    """Calculate (a//b, a%b) """
    if isinstance(b, ev.EUDVariable):
        return _f_div(a, b)

    elif isinstance(a, ev.EUDVariable):
        return f_constdiv(b)(a)

    else:
        if b:
            q, m = a // b, a % b
        else:
            q, m = 0xFFFFFFFF, a
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
    if not hasattr(f_constmul, "mulfdict"):
        f_constmul.mulfdict = {}

    mulfdict = f_constmul.mulfdict

    try:
        return mulfdict[number]
    except KeyError:

        @ef.EUDFunc
        def _mulf(a):
            ret = ev.EUDVariable()
            ret << 0
            for i in range(31, -1, -1):
                rt.RawTrigger(
                    conditions=a.AtLeast(2 ** i),
                    actions=[a.SubtractNumber(2 ** i), ret.AddNumber(2 ** i * number)],
                )
            return ret

        mulfdict[number] = _mulf
        return _mulf


def f_constdiv(number):
    """
    f_constdiv(a)(b) calculates (b // a, b % a)

    :param number: Constant integer to divide other numbers by.
    :return: Function taking one parameter.
    """
    if not hasattr(f_constdiv, "divfdict"):
        f_constdiv.divfdict = {}

    divfdict = f_constdiv.divfdict

    try:
        return divfdict[number]
    except KeyError:

        @ef.EUDFunc
        def _divf(a):
            ret = ev.EUDVariable()
            ret << 0
            for i in range(31, -1, -1):
                # number too big
                if 2 ** i * number >= 2 ** 32:
                    continue

                rt.RawTrigger(
                    conditions=a.AtLeast(2 ** i * number),
                    actions=[a.SubtractNumber(2 ** i * number), ret.AddNumber(2 ** i)],
                )
            return ret, a

        divfdict[number] = _divf
        return _divf


# -------


@ef.EUDFunc
def _f_mul(a, b):
    ret, y0 = ev.EUDCreateVariables(2)

    # Init
    ev.SeqCompute([(ret, rt.SetTo, 0), (y0, rt.SetTo, b)])

    chain = [ac.Forward() for _ in range(32)]
    chain_y0 = [ac.Forward() for _ in range(32)]

    # Calculate chain_y0
    for i in range(32):
        ev.SeqCompute(((ut.EPD(chain_y0[i]), rt.SetTo, y0), (y0, rt.Add, y0)))
        if i <= 30:
            p1, p2, p3 = ac.Forward(), ac.Forward(), ac.Forward()
            p1 << rt.RawTrigger(
                nextptr=p2,
                conditions=a.AtMost(2 ** (i + 1) - 1),
                actions=rt.SetNextPtr(p1, p3),
            )
            p3 << rt.RawTrigger(nextptr=chain[i], actions=rt.SetNextPtr(p1, p2))
            p2 << rt.NextTrigger()

    # Run multiplication chain
    for i in range(31, -1, -1):
        cy0 = ac.Forward()

        chain[i] << rt.RawTrigger(
            conditions=[a.AtLeast(2 ** i)],
            actions=[a.SubtractNumber(2 ** i), cy0 << ret.AddNumber(0)],
        )

        chain_y0[i] << cy0 + 20

    return ret


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
            nextptr=p2, conditions=x.AtLeast(0x80000000), actions=rt.SetNextPtr(p1, p3)
        )
        p3 << rt.RawTrigger(nextptr=chain[i], actions=rt.SetNextPtr(p1, p2))
        p2 << rt.NextTrigger()

        ev.SeqCompute([(x, rt.Add, x)])

    # Run division chain
    for i in range(31, -1, -1):
        cx0, cx1 = ac.Forward(), ac.Forward()
        chain[i] << rt.RawTrigger(
            conditions=[cx0 << a.AtLeast(0)],
            actions=[cx1 << a.SubtractNumber(0), ret.AddNumber(2 ** i)],
        )

        chain_x0[i] << cx0 + 8
        chain_x1[i] << cx1 + 20

    return ret, a  # a : remainder
