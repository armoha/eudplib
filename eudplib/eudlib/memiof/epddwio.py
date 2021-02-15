#!/usr/bin/python
# -*- coding: utf-8 -*-

import random
from ... import core as c, ctrlstru as cs, utils as ut

from .modcurpl import f_setcurpl2cpcache
from ...core.eudfunc.eudf import _EUDPredefineParam
from ...core.variable.evcommon import _ev


def bits(n):
    n = n & 0xFFFFFFFF
    while n:
        b = n & (~n + 1)
        yield b
        n ^= b


@_EUDPredefineParam(_ev[2:3])
@c.EUDFunc
def f_cunitepdread_epd(targetplayer):
    epd, ptr = c.EUDCreateVariables(2)
    u = random.randint(234, 65535)
    acts = [
        targetplayer.SetDest(ut.EPD(0x6509B0)),  # TODO: 게임 시작 때 dest 초기화하기
        targetplayer.AddNumber(-12 * u),
        epd.SetNumber(ut.EPD(0)),
        epd.SetDest(ptr),
        ptr.QueueAddTo(ptr),
    ]
    c.VProc(targetplayer, ut.RandList(acts))

    for bit in bits(0x7FFFF8):
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, u, bit),
            actions=epd.AddNumber(bit // 4),
        )

    c.VProc([epd, ptr], [])  # 2 * epd
    f_setcurpl2cpcache(ptr, ptr.AddNumber(0x58A364 // 2))  # ptr = 4 * epd + 0x58A364

    return ptr, epd


@_EUDPredefineParam(_ev[2:3])
@c.EUDFunc
def f_dwepdread_epd(targetplayer):
    epd, ptr = c.EUDCreateVariables(2)
    u = random.randint(234, 65535)
    acts = [
        targetplayer.SetDest(ut.EPD(0x6509B0)),  # TODO: 게임 시작 때 dest 초기화하기
        targetplayer.AddNumber(-12 * u),
        epd.SetNumber(ut.EPD(0)),
        epd.SetDest(ptr),
        ptr.QueueAddTo(ptr),
    ]
    c.VProc(targetplayer, ut.RandList(acts))

    for i in ut.RandList(range(2, 32)):
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, u, 2 ** i),
            actions=epd.AddNumber(2 ** (i - 2)),
        )

    c.VProc([epd, ptr], [])  # 2 * epd
    f_setcurpl2cpcache(ptr, ptr.AddNumber(0x58A364 // 2))  # ptr = 4 * epd + 0x58A364

    return ptr, epd


@c.EUDFunc
def _cunitepdread_cp():
    epd, ptr = c.EUDCreateVariables(2)
    acts = [
        epd.SetNumber(ut.EPD(0)),
        epd.SetDest(ptr),
        ptr.QueueAddTo(ptr),
    ]
    cs.DoActions(ut.RandList(acts))

    for bit in bits(0x7FFFF8):
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, bit),
            actions=epd.AddNumber(bit // 4),
        )

    c.VProc([epd, ptr], [])  # 2 * epd
    c.VProc(ptr, ptr.AddNumber(0x58A364 // 2))  # ptr = 4 * epd + 0x58A364

    return ptr, epd


def f_cunitepdread_cp(cpo, **kwargs):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    ptr, epd = _cunitepdread_cp(**kwargs)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return ptr, epd


@c.EUDFunc
def _reader():
    epd, ptr = c.EUDCreateVariables(2)
    acts = [
        epd.SetNumber(ut.EPD(0)),
        epd.SetDest(ptr),
        ptr.QueueAddTo(ptr),
    ]
    cs.DoActions(ut.RandList(acts))

    for i in ut.RandList(range(2, 32)):
        c.RawTrigger(
            conditions=c.DeathsX(c.CurrentPlayer, c.AtLeast, 1, 0, 2 ** i),
            actions=epd.AddNumber(2 ** (i - 2)),
        )

    c.VProc([epd, ptr], [])  # 2 * epd
    c.VProc(ptr, ptr.AddNumber(0x58A364 // 2))  # ptr = 4 * epd + 0x58A364

    return ptr, epd


def f_dwepdread_cp(cpo, **kwargs):
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, cpo))
    ptr, epd = _reader(**kwargs)
    if not (isinstance(cpo, int) and cpo == 0):
        cs.DoActions(c.SetMemory(0x6509B0, c.Add, -cpo))
    return ptr, epd
