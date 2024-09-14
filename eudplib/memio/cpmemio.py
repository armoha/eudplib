# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..core.eudfunc.eudf import _EUDPredefineReturn
from ..core.variable.evcommon import _ev
from . import dwepdio as dwm
from . import modcurpl as cp


@_EUDPredefineReturn(2)
@c.EUDFunc
def _reader():
    ptr, epd = _reader._frets
    cs.DoActions(ptr.SetNumber(0), epd.SetNumber(ut.EPD(0)))
    for i in ut._rand_lst(range(32)):
        c.RawTrigger(
            conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**i),
            actions=[
                ptr.AddNumber(2**i),
                epd.AddNumber(2 ** (i - 2)),
            ]
            if i >= 2
            else ptr.AddNumber(2**i),
        )

    # return ptr, epd


def f_dwepdread_cp(cpo, **kwargs):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    ptr, epd = _reader(**kwargs)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return ptr, epd


def f_dwread_cp(cpo, **kwargs):
    ret = kwargs.get("ret")
    if ret is not None:
        ret.append(_ev[4])
    return f_dwepdread_cp(cpo, **kwargs)[0]


def f_epdread_cp(cpo, **kwargs):
    ret = kwargs.get("ret")
    if ret is not None:
        ret.insert(0, _ev[4])
    return f_dwepdread_cp(cpo, **kwargs)[1]


@_EUDPredefineReturn(1)
@c.EUDFunc
def _wreader(subp):
    w = _wreader._frets[0]
    w << 0
    cs.EUDSwitch(subp)
    for bits in ut._rand_lst(range(3)):
        if cs.EUDSwitchCase()(bits):
            byte = 8 * bits
            for power in ut._rand_lst(range(byte, byte + 16)):
                c.RawTrigger(
                    conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**power),
                    actions=w.AddNumber(2 ** (power - byte)),
                )
            cs.EUDBreak()
    if cs.EUDSwitchCase()(3):
        for power in ut._rand_lst(range(24, 32)):
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**power),
                actions=w.AddNumber(2 ** (power - 24)),
            )
        c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, 1))
        for power in ut._rand_lst(range(8)):
            c.RawTrigger(
                conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**power),
                actions=w.AddNumber(2 ** (power + 8)),
            )
        c.RawTrigger(actions=c.SetMemory(0x6509B0, c.Add, -1))
        cs.EUDBreak()
    cs.EUDEndSwitch()
    # return w


def f_wread_cp(cpo, subp, **kwargs):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    w = _wreader(subp, **kwargs)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return w


@c.EUDFunc
def _breader(subp):
    b = c.EUDVariable()
    b << 0
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            for j in ut._rand_lst(range(8 * i, 8 * i + 8)):
                c.RawTrigger(
                    conditions=c.DeathsX(cp.CP, c.AtLeast, 1, 0, 2**j),
                    actions=b.AddNumber(2 ** (j - 8 * i)),
                )

            cs.EUDBreak()
    cs.EUDEndSwitch()
    return b


def f_bread_cp(cpo, subp, **kwargs):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    b = _breader(subp, **kwargs)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return b


def f_dwwrite_cp(cpo, value):
    if isinstance(cpo, int) and cpo == 0 and c.IsEUDVariable(value):
        c.VProc(value, value.QueueAssignTo(cp.CP))
    elif isinstance(cpo, int) and cpo == 0:
        cs.DoActions(c.SetDeaths(cp.CP, c.SetTo, value, 0))
    else:
        cs.DoActions(
            c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeaths(cp.CP, c.SetTo, value, 0),
            c.SetMemory(0x6509B0, c.Add, -cpo),
        )


def f_dwadd_cp(cpo, value):
    if isinstance(cpo, int) and cpo == 0 and c.IsEUDVariable(value):
        c.VProc(value, value.QueueAddTo(cp.CP))
    elif isinstance(cpo, int) and cpo == 0:
        cs.DoActions(c.SetDeaths(cp.CP, c.Add, value, 0))
    else:
        cs.DoActions(
            c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeaths(cp.CP, c.Add, value, 0),
            c.SetMemory(0x6509B0, c.Add, -cpo),
        )


def f_dwsubtract_cp(cpo, value):
    if isinstance(cpo, int) and cpo == 0 and c.IsEUDVariable(value):
        c.VProc(value, value.QueueSubtractTo(cp.CP))
    elif isinstance(cpo, int) and cpo == 0:
        cs.DoActions(c.SetDeaths(cp.CP, c.Subtract, value, 0))
    else:
        cs.DoActions(
            c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeaths(cp.CP, c.Subtract, value, 0),
            c.SetMemory(0x6509B0, c.Add, -cpo),
        )


@c.EUDFunc
def _wwriter(subp, w):
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(3)):
        if cs.EUDSwitchCase()(i):
            c.RawTrigger(actions=c.SetDeathsX(cp.CP, c.SetTo, 0, 0, 65535 << (8 * i)))
            c.SeqCompute([(cp.CP, c.Add, w * (256**i))])
            cs.EUDBreak()

    # Things gets complicated on this case.
    # We won't hand-optimize this case. This is a very, very rare case
    if cs.EUDSwitchCase()(3):
        b0, b1 = dwm.f_dwbreak(w)[2:4]
        f_bwrite_cp(0, 3, b0)
        f_bwrite_cp(1, 0, b1)

    cs.EUDEndSwitch()


def f_wwrite_cp(cpo, subp, w):
    try:
        cs.DoActions(
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeathsX(
                cp.CP,
                c.SetTo,
                w * (256**subp),
                0,
                65535 << (8 * subp),
            ),
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, -cpo),
        )
    except TypeError:
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
        _wwriter(subp, w)
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))


@c.EUDFunc
def _bwriter(subp, b):
    cs.EUDSwitch(subp)
    for i in ut._rand_lst(range(4)):
        if cs.EUDSwitchCase()(i):
            c.RawTrigger(actions=c.SetDeathsX(cp.CP, c.SetTo, 0, 0, 255 << (8 * i)))

            c.SeqCompute([(cp.CP, c.Add, b * (256**i))])
            cs.EUDBreak()
    cs.EUDEndSwitch()
    return b


def f_bwrite_cp(cpo, subp, b):
    try:
        cs.DoActions(
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeathsX(
                cp.CP,
                c.SetTo,
                b * (256**subp),
                0,
                255 << (8 * subp),
            ),
            []
            if isinstance(cpo, int) and cpo == 0
            else c.SetMemory(0x6509B0, c.Add, -cpo),
        )
    except TypeError:
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
        _bwriter(subp, b)
        if not (isinstance(cpo, int) and cpo == 0):
            cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))


def f_maskwrite_cp(cpo, value, mask):
    if isinstance(cpo, int) and cpo == 0:
        cs.DoActions(c.SetDeathsX(cp.CP, c.SetTo, value, 0, mask))
    else:
        cs.DoActions(
            c.SetMemory(0x6509B0, c.Add, cpo),
            c.SetDeathsX(cp.CP, c.SetTo, value, 0, mask),
            c.SetMemory(0x6509B0, c.Add, -cpo),
        )
