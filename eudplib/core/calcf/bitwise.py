#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ...utils import EPD, _rand_lst
from .. import allocator as ac
from .. import eudfunc as ef
from .. import rawtrigger as rt
from .. import variable as ev
from ..eudfunc.eudf import _EUDPredefineParam, _EUDPredefineReturn
from ..variable import SeqCompute
from ..variable.evcommon import _selfadder, _xv
from .muldiv import _quot

_x = _xv[0]


def f_bitand(a, b):
    """Calculate a & b"""
    return a & b


def f_bitor(a, b):
    """Calculate a | b"""
    return a | b


def f_bitxor(a, b):
    """Calculate a ^ b"""
    return a ^ b


def f_bitnand(a, b):
    """Calculate ~(a & b)"""
    try:
        return (a & b).iinvert()
    except AttributeError:
        return ~(a & b)


def f_bitnor(a, b):
    """Calculate ~(a | b)"""
    try:
        return (a | b).iinvert()
    except AttributeError:
        return ~(a | b)


def f_bitnxor(a, b):
    """Calculate ~(a ^ b)"""
    return f_bitxor(a, ~b)


def f_bitnot(a):
    """Calculate ~a"""
    return ~a


# -------


@ef.EUDFunc
def f_bitsplit(a):
    """Splits bit of given number

    :returns: int bits[32];  // bits[i] = (ith bit from LSB of a is set)
    """
    bits = ev.EUDCreateVariables(32)
    rt.RawTrigger(actions=[bits[i].SetNumber(0) for i in range(32)])
    for i in range(31, -1, -1):
        rt.RawTrigger(conditions=a.AtLeastX(1, 2**i), actions=bits[i].SetNumber(1))
    return bits


# -------


@_EUDPredefineParam(1)
@_EUDPredefineReturn(1, 2)
@ef.EUDFunc
def _exp2_vv(n):
    ret = _exp2_vv._frets[0]
    ret << 0
    for i in _rand_lst(range(32)):
        rt.RawTrigger(conditions=[n == i], actions=ret.SetNumber(2**i))
    # return ret


def _exp2(n):
    if isinstance(n, int):
        if n >= 32:
            return 0
        return 1 << n

    return _exp2_vv(n)


@ef.EUDFunc
def _f_bitrshift(a, b):
    ret = ev.EUDVariable()

    skip_check = ac.Forward()
    exponential = ac.Forward()
    skip_to_here = ac.Forward()
    return_function = ac.Forward()

    skip_check << rt.RawTrigger(
        nextptr=exponential,
        conditions=b.AtLeast(32),
        actions=[ret.SetNumber(0), rt.SetNextPtr(skip_check, skip_to_here)],
    )
    skip_to_here << rt.RawTrigger(
        nextptr=return_function, actions=rt.SetNextPtr(skip_check, exponential)
    )
    exponential << rt.NextTrigger()
    ret << _quot(a, _exp2_vv(b))
    return_function << rt.NextTrigger()
    return ret


@ef.EUDFunc
def _f_bitlshift(a, b):
    loopstart = ac.Forward()
    loopend = ac.Forward()
    loopcnt = ac.Forward()

    rt.RawTrigger(actions=[rt.SetNextPtr(a.GetVTable(), loopcnt), a.QueueAddTo(a)])

    loopstart << rt.RawTrigger(
        nextptr=loopend,
        conditions=[a.AtLeast(1), b.AtLeast(1)],
        actions=rt.SetNextPtr(loopstart, a.GetVTable()),
    )
    loopcnt << rt.RawTrigger(
        nextptr=loopstart,
        actions=[b.SubtractNumber(1), rt.SetNextPtr(loopstart, loopend)],
    )
    loopend << rt.NextTrigger()

    return a


def f_bitlshift(a, b, _fdict={}, **kwargs):
    """Calculate a << b"""
    if not ev.IsEUDVariable(a) and not ev.IsEUDVariable(b):
        if "ret" in kwargs:
            SeqCompute((kwargs["ret"][0], rt.SetTo, a << b))
            return kwargs["ret"][0]
        return a << b
    ret = kwargs["ret"][0] if "ret" in kwargs else ev.EUDVariable()
    if ev.IsEUDVariable(a) and not ev.IsEUDVariable(b):
        if b == 0:
            if a is ret:
                return a
            ev.SeqCompute([(ret, rt.SetTo, a)])
        elif 1 <= b <= 10:
            try:
                f = _fdict[b]
            except KeyError:
                set_ret = _selfadder.SetDest(0)

                @_EUDPredefineParam((EPD(set_ret) + 5, _selfadder))
                @ef.EUDFunc
                def f(ret, adder):
                    for i in range(b):
                        ev.VProc(adder, [])
                    ev.VProc(
                        adder,
                        [
                            set_ret,
                            adder.SetModifier(rt.SetTo),
                        ],
                    )
                    rt.RawTrigger(
                        actions=[
                            adder.SetDest(EPD(adder.getValueAddr())),
                            adder.SetModifier(rt.Add),
                        ]
                    )

                _fdict[b] = f

            if ev.IsEUDVariable(ret):
                retarg = EPD(ret.getValueAddr())
            else:
                retarg = ret
            if "ret" in kwargs:
                del kwargs["ret"]
            f(retarg, a, **kwargs)
        else:
            if a is not ret:
                ev.SeqCompute([(ret, rt.SetTo, a)])
            ev.vbase.VariableBase.__ilshift__(ret, b)
        return ret

    return _f_bitlshift(a, b, **kwargs)


def f_bitrshift(a, b, **kwargs):
    """Calculate a >> b"""
    if not ev.IsEUDVariable(a) and not ev.IsEUDVariable(b):
        if "ret" in kwargs:
            SeqCompute((kwargs["ret"][0], rt.SetTo, a >> b))
            return kwargs["ret"][0]
        return a >> b
    ret = kwargs["ret"][0] if "ret" in kwargs else ev.EUDVariable()
    if ev.IsEUDVariable(a) and not ev.IsEUDVariable(b):
        if b == 0:
            if a is ret:
                return a
            ev.SeqCompute([(ret, rt.SetTo, a)])
        else:
            if a is not ret:
                ev.SeqCompute([(ret, rt.SetTo, a)])
            ev.vbase.VariableBase.__irshift__(ret, b)
        return ret

    return _f_bitrshift(a, b, **kwargs)
