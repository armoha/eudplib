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

from .. import allocator as ac
from .. import variable as ev
from .. import eudfunc as ef
from .. import rawtrigger as rt
from .muldiv import f_mul
from ...utils import EPD, RandList
from ..eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from ..variable.evcommon import _xv

_x = _xv[0]


def f_bitand(a, b):
    """Calculate a & b"""
    ret = ev.EUDVariable()

    assignPairs = [
        (ret, rt.SetTo, 0),
        (_x, rt.SetTo, a),
        (EPD(_x.getMaskAddr()), rt.SetTo, b),
        (ret, rt.SetTo, _x),
    ]
    if not ev.IsEUDVariable(b):
        assignPairs[1], assignPairs[2] = assignPairs[2], assignPairs[1]
    ev.SeqCompute(assignPairs)

    return ret


def f_bitor(a, b):
    """Calculate a | b"""
    ret = ev.EUDVariable()

    assignPairs = [
        (_x, rt.SetTo, ~0),
        (ret, rt.SetTo, a),
        (EPD(_x.getMaskAddr()), rt.SetTo, b),
        (ret, rt.SetTo, _x),
    ]
    if not ev.IsEUDVariable(b):
        assignPairs[1], assignPairs[2] = assignPairs[2], assignPairs[1]
    ev.SeqCompute(assignPairs)

    return ret


@ef.EUDFunc
def f_bitxor(a, b):
    """Calculate a ^ b"""
    assignPairs = [
        (_x, rt.SetTo, ~0),
        (_x, rt.Subtract, a),
        (EPD(_x.getMaskAddr()), rt.SetTo, b),
        (a, rt.SetTo, _x),  # (~a & b) + (a & ~b)
    ]
    ev.SeqCompute(assignPairs)

    return a


def f_bitnand(a, b):
    """Calculate ~(a & b)"""
    ret = ev.EUDVariable()
    assignPairs = [
        (ret, rt.SetTo, ~0),
        (_x, rt.SetTo, a),
        (EPD(_x.getMaskAddr()), rt.SetTo, b),
        (ret, rt.Subtract, _x),  # (~a & b) + (a & ~b)
    ]
    if not ev.IsEUDVariable(b):
        assignPairs[1], assignPairs[2] = assignPairs[2], assignPairs[1]
    ev.SeqCompute(assignPairs)

    return ret


def f_bitnor(a, b):
    """Calculate ~(a | b)"""
    ret = ev.EUDVariable()

    assignPairs = [
        (ret, rt.SetTo, ~0),
        (_x, rt.SetTo, 0),
        (ret, rt.Subtract, a),
        (EPD(_x.getMaskAddr()), rt.SetTo, b),
        (ret, rt.SetTo, _x),
    ]
    if not ev.IsEUDVariable(b):
        assignPairs[1], assignPairs[2] = assignPairs[2], assignPairs[1]
    ev.SeqCompute(assignPairs)

    return ret


def f_bitnxor(a, b):
    """Calculate ~(a ^ b)"""
    return f_bitnot(f_bitxor(a, b))


def f_bitnot(a):
    """Calculate ~a"""
    return 0xFFFFFFFF - a


# -------


@ef.EUDFunc
def f_bitsplit(a):
    """Splits bit of given number

    :returns: int bits[32];  // bits[i] = (ith bit from LSB of a is set)
    """
    bits = ev.EUDCreateVariables(32)
    rt.RawTrigger(actions=[bits[i].SetNumber(0) for i in range(32)])
    for i in range(31, -1, -1):
        rt.RawTrigger(conditions=a.AtLeastX(1, 2 ** i), actions=bits[i].SetNumber(1))
    return bits


# -------


@_EUDPredefineParam(1)
@_EUDPredefineReturn(1, 2)
@ef.EUDFunc
def _exp2_vv(n):
    ret = _exp2_vv._frets[0]
    ret << 0
    for i in RandList(range(32)):
        rt.RawTrigger(conditions=[n == i], actions=ret.SetNumber(2 ** i))
    # return ret


def _exp2(n):
    if isinstance(n, int):
        if n >= 32:
            return 0
        return 1 << n

    return _exp2_vv(n)


@ef.EUDFunc
def _f_bitlshift(a, b):
    loopstart = ac.Forward()
    loopend = ac.Forward()
    loopcnt = ac.Forward()

    rt.RawTrigger(actions=[rt.SetNextPtr(a.GetVTable(), loopcnt), a.QueueAddTo(a)])

    loopstart << rt.RawTrigger(
        nextptr=a.GetVTable(),
        conditions=b.Exactly(0),
        actions=rt.SetNextPtr(loopstart, loopend),
    )
    loopcnt << rt.RawTrigger(nextptr=loopstart, actions=b.SubtractNumber(1))
    loopend << rt.RawTrigger(actions=rt.SetNextPtr(loopstart, a.GetVTable()))

    return a


def f_bitlshift(a, b, **kwargs):
    """Calculate a << b"""
    if isinstance(b, int):
        if 1 <= b <= 7:
            return _f_bitlshift(a, b, **kwargs)
        else:
            return f_mul(a, _exp2(b), **kwargs)
    return _f_bitlshift(a, b, **kwargs)


def f_bitrshift(a, b):
    """Calculate a >> b"""
    if isinstance(b, int) and b >= 32:
        return 0

    return a // _exp2(b)
