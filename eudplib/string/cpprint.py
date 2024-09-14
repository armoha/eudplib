#!/usr/bin/python
# Copyright 2014-2019 by trgk, Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from math import ceil

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

from ..collections.eudarray import EUDArray
from ..eudlib.utilf.userpl import IsUserCP
from ..memio import (
    CPByteWriter,
    f_bread_epd,
    f_cunitread_epd,
    f_getcurpl,
    f_setcurpl,
)
from ..memio.rwcommon import br1
from ..scdata.scdata import CurrentPlayer, TrgPlayer
from .cpstr import CPString, _s2b
from .dbstr import DBString
from .eudprint import _conststr_dict, epd2s, hptr, ptr2s

cw = CPByteWriter()
prevcp = c.EUDVariable()


@c.EUDFunc
def _pcolor(p):
    p += ut.EPD(0x581D76)
    pcolor = f_bread_epd(p, 2)
    # fmt: off
    pt_arr = EUDArray([
        21, 14, 16, 14, 14, 14, 14, 28, 16, 14, 28, 28, 28, 28, 16, 16,
        21, 21, 21, 21, 21, 21, 21,  6, 21, 21, 21,  8, 17, 17,  8, 17,
        17,  3, 24, 24, 24, 24, 29, 29, 14, 14, 14, 14, 14, 14, 14, 14,
        28, 28, 28, 28, 31, 14, 28, 31, 31, 31, 31, 31, 22, 23, 25, 25,
        21, 21, 21, 21, 21, 14, 21, 21, 21, 16, 30, 29, 29, 29, 30, 29,
        29, 22, 22, 22, 22,  4, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21,
        21, 24, 21, 21, 21, 24, 21,  6, 17, 21, 29, 17,  6, 17,  8,  8,
         8,  8, 27, 17,  3,  7, 14, 16, 14, 14, 14, 14, 14, 28, 28,  2,
        31, 29, 29,  3,  3,  3, 27, 23, 25, 25, 21, 21, 21, 21, 21, 21,
        21, 16, 16, 24, 21, 28, 30, 30, 27, 27, 30,  2, 17, 24, 15, 15,
        14, 16, 14, 16, 16, 14,  3,  3, 21, 21, 21, 21, 21, 21,  6,  8,
         6,  8,  8, 17, 17, 21, 24, 24, 24, 24, 24, 24, 29, 29, 29, 29,
        14, 14, 14, 28, 28, 28, 30,  2, 21, 21, 21, 21, 21, 14, 14, 21,
        21, 21, 21, 21, 21, 21, 21, 29, 21, 21, 21, 21, 21, 21, 21, 21,
        21, 21, 21, 21, 24, 24, 24, 16, 14, 14, 21, 21, 21, 21, 21, 21,
        21, 21, 21, 21, 21, 21, 14, 21, 21, 21, 14, 28, 28, 28,  4,  4,
    ])
    # fmt: on
    pcolor += ut.EPD(pt_arr)
    return pcolor


def PColor(i):  # noqa: N802
    if isinstance(i, TrgPlayer):
        i = c.EncodePlayer(i)
        if not c.IsEUDVariable(i) and i == CurrentPlayer:
            i = prevcp
    return epd2s(_pcolor(i * 2))


def PName(x):  # noqa: N802
    if isinstance(x, TrgPlayer):
        x = c.EncodePlayer(x)
        if not c.IsEUDVariable(x) and x == CurrentPlayer:
            x = prevcp
    return ptr2s(0x57EEEB + 36 * x)


class FixedText:
    def __init__(self, actions_on_exit=[]):
        self._actions_on_exit = ut.FlattenList([actions_on_exit])
        self._txtptr = c.EUDXVariable(ut.EPD(0x640B58), c.SetTo, 0)

    def __enter__(self):
        f_gettextptr(ret=[self._txtptr])
        return self._txtptr

    def __exit__(self, exc_type, exc_value, traceback):
        c.VProc(self._txtptr, self._actions_on_exit)


@c.EUDFunc
def f_gettextptr():
    ret = c.EUDVariable()
    ret << 0
    for i in range(3, -1, -1):
        c.RawTrigger(
            conditions=c.MemoryX(0x640B58, c.AtLeast, 1, 2**i),
            actions=ret.AddNumber(2**i),
        )
    return ret


@c.EUDFunc
def f_getnextchatdst():
    ret = c.EUDVariable()
    ret << ut.EPD(0x640B60)
    for i in range(3, -1, -1):
        c.RawTrigger(
            conditions=c.MemoryX(0x640B58, c.AtLeast, 1, 2**i),
            actions=ret.AddNumber(ceil((2**i) * 54.5)),
        )
    return ret


@c.EUDFunc
def _addstr_cp():
    b = c.EUDVariable()
    if cs.EUDInfLoop()():
        b = br1.readbyte()
        cs.EUDBreakIf(b == 0)
        cw.writebyte(b)
    cs.EUDEndInfLoop()

    cw.flushdword()


@c.EUDFunc
def f_cpstr_addstr(src):
    """Print string as string to CurrentPlayer

    :param src: Source address (Not EPD player)
    """
    br1.seekoffset(src)
    _addstr_cp()


@c.EUDFunc
def f_cpstr_addstr_epd(epd):
    """Print string as string to CurrentPlayer

    :param epd: EPD player of Source address
    """
    br1.seekepd(epd)
    _addstr_cp()


@c.EUDFunc
def f_cpstr_adddw(number):
    """Print number as string to CurrentPlayer.

    :param number: DWORD to print
    """
    skipper = [c.Forward() for _ in range(9)]
    ch = [0] * 10

    # Get digits
    for i in range(10):
        number, ch[i] = c.f_div(number, 10)
        if i != 9:
            cs.EUDJumpIf(number == 0, skipper[i])

    # print digits
    for i in range(9, -1, -1):
        if i != 9:
            skipper[i] << c.NextTrigger()
        cw.writebyte(ch[i] + b"0"[0])

    cw.flushdword()


@c.EUDFunc
def f_cpstr_addptr(number):
    """Print number as string to CurrentPlayer.

    :param number: DWORD to print
    """
    digit = [c.EUDLightVariable() for _ in range(8)]
    cs.DoActions(
        *[digit[i].SetNumber(0) for i in range(8)],
        c.SetDeaths(CurrentPlayer, c.SetTo, ut.b2i4(b"0000"), 0),
    )

    def f(x):
        t = x % 16
        q, r = divmod(t, 4)
        return 2 ** (r + 8 * (3 - q))

    for i in range(31, -1, -1):
        c.RawTrigger(
            conditions=number.AtLeastX(1, 2**i),
            actions=[
                digit[i // 4].AddNumber(2 ** (i % 4)),
                c.SetDeaths(CurrentPlayer, c.Add, f(i), 0),
            ],
        )
        if i % 16 == 0:
            for j in range(4):
                c.RawTrigger(
                    conditions=digit[j + 4 * (i // 16)].AtLeast(10),
                    actions=c.SetDeaths(
                        CurrentPlayer,
                        c.Add,
                        (b"A"[0] - b":"[0]) * (256 ** (3 - j)),
                        0,
                    ),
                )
            if i == 16:
                cs.DoActions(
                    *c.AddCurrentPlayer(1),
                    c.SetDeaths(CurrentPlayer, c.SetTo, ut.b2i4(b"0000"), 0),
                )
            else:
                cs.DoActions(*c.AddCurrentPlayer(1))


def f_cpstr_print(*args, EOS=True, encoding="UTF-8"):  # noqa: N803
    """Print multiple string / number to CurrentPlayer.

    :param args: Things to print

    """
    args = ut.FlattenList(args)
    for arg in args:
        try:
            arg = arg.fmt()
        except AttributeError:
            pass
        if ut.isUnproxyInstance(arg, str):
            arg = arg.encode(encoding)
        elif ut.isUnproxyInstance(arg, int):
            arg = ut.u2utf8(str(arg & 0xFFFFFFFF))
        if ut.isUnproxyInstance(arg, bytes):
            key = _s2b(arg)
            if key not in _conststr_dict:
                _conststr_dict[key] = c.Db(arg + b"\0")
            arg = _conststr_dict[key]
        if ut.isUnproxyInstance(arg, CPString):
            arg.Display()
        elif ut.isUnproxyInstance(arg, c.Db):
            f_cpstr_addstr_epd(ut.EPD(arg))
        elif ut.isUnproxyInstance(arg, ptr2s):
            f_cpstr_addstr(arg._value)
        elif ut.isUnproxyInstance(arg, epd2s):
            f_cpstr_addstr_epd(arg._value)
        elif ut.isUnproxyInstance(arg, DBString):
            f_cpstr_addstr_epd(ut.EPD(arg.GetStringMemoryAddr()))
        elif c.IsEUDVariable(arg) or c.IsConstExpr(arg):
            f_cpstr_adddw(arg)
        elif ut.isUnproxyInstance(arg, hptr):
            f_cpstr_addptr(arg._value)
        else:
            raise ut.EPError(
                f"Object with unknown parameter type {type(arg)} given to f_cpprint."
            )
    if EOS:
        cs.DoActions(c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0))


@c.EUDTypedFunc([TrgPlayer])
def f_raise_CCMU(player):  # noqa: N802
    if cs.EUDIf()(c.Memory(0x628438, c.AtLeast, 0x59CCA8)):
        orignextptr = f_cunitread_epd(ut.EPD(0x628438))
        print_error = c.Forward()
        c.VProc(player, player.SetDest(ut.EPD(print_error + 16)))
        c.VProc(
            orignextptr,  # restores 0x628438
            [
                c.SetMemory(0x628438, c.SetTo, 0),
                print_error << c.CreateUnit(1, 0, 64, 0),
                orignextptr.SetDest(ut.EPD(0x628438)),
            ],
        )
    if cs.EUDElse()():
        cs.DoActions(c.CreateUnit(1, 0, 64, player))
    cs.EUDEndIf()


_eprintln_template = c.Forward()
_eprintln_desync = c.Forward()
_eprintln_print = c.Forward()
_eprintln_eos = c.Forward()
_eprintln_end = c.Forward()


def _eprint_init():
    if _eprintln_template.IsSet():
        return
    c.PushTriggerScope()
    _eprintln_template << c.NextTrigger()
    f_raise_CCMU(CurrentPlayer)
    if cs.EUDIf()(_eprintln_desync << IsUserCP()):
        prevcp << f_getcurpl()
        _eprintln_print << c.RawTrigger(
            nextptr=0, actions=c.SetCurrentPlayer(ut.EPD(0x640B60 + 218 * 12))
        )
        _eprintln_eos << c.RawTrigger(
            actions=c.SetDeaths(CurrentPlayer, c.SetTo, 0, 0)
        )
        f_setcurpl(prevcp)
    cs.EUDEndIf()
    _eprintln_end << c.RawTrigger(nextptr=0)
    c.PopTriggerScope()


def eprint_all(*args):
    _eprint_init()

    _print, _next = c.Forward(), c.Forward()
    c.RawTrigger(
        nextptr=_eprintln_template,
        actions=[
            c.SetMemory(_eprintln_template + 380, c.SetTo, 17),  # AllPlayers
            c.SetMemoryX(_eprintln_desync + 12, c.SetTo, 0, 0xFF000000),
            c.SetNextPtr(_eprintln_print, _print),
            c.SetNextPtr(_eprintln_end, _next),
        ],
    )
    _print << c.NextTrigger()
    f_cpstr_print(*args, EOS=False, encoding="UTF-8")
    c.SetNextTrigger(_eprintln_eos)
    _next << c.NextTrigger()


def f_eprintln(*args):
    _eprint_init()

    _print, _next = c.Forward(), c.Forward()
    c.RawTrigger(
        nextptr=_eprintln_template,
        actions=[
            c.SetMemory(
                _eprintln_template + 380,
                c.SetTo,
                c.EncodePlayer(CurrentPlayer),
            ),
            c.SetMemoryX(_eprintln_desync + 12, c.SetTo, 15 << 24, 0xFF000000),
            c.SetNextPtr(_eprintln_print, _print),
            c.SetNextPtr(_eprintln_end, _next),
        ],
    )
    _print << c.NextTrigger()
    f_cpstr_print(*args, EOS=False, encoding="UTF-8")
    c.SetNextTrigger(_eprintln_eos)
    _next << c.NextTrigger()
