#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2014 trgk, 2019 Armoha

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

from eudplib import core as c, ctrlstru as cs, utils as ut

from ..memiof import CPByteWriter, f_setcurpl, f_getcurpl, f_dwwrite, f_cunitread_epd, f_bread_epd
from ..rwcommon import br1
from .cpstr import _s2b, CPString
from .dbstr import DBString
from .eudprint import ptr2s, epd2s, hptr, _conststr_dict
from .tblprint import GetTBLAddr
from ..eudarray import EUDArray

cw = CPByteWriter()
prevcp = c.EUDVariable()


@c.EUDFunc
def _PColor(p):
    p = c.f_bitlshift(p, 1)
    pcolor = f_bread_epd(ut.EPD(0x581D76) + p, 2)
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
    c.EUDReturn(ut.EPD(pt_arr) + pcolor)


def PColor(i):
    if type(i) == type(c.P1) and i == c.CurrentPlayer:
        i = prevcp
    return epd2s(_PColor(i))


def PName(x):
    if ut.isUnproxyInstance(x, type(c.P1)):
        x = c.EncodePlayer(x)
        if x == c.EncodePlayer(c.CurrentPlayer):
            x = prevcp
    return ptr2s(0x57EEEB + 36 * x)


@c.EUDFunc
def _addstr_cp():
    b = c.EUDVariable()
    if cs.EUDInfLoop()():
        c.SetVariables(b, br1.readbyte())
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
        [
            [digit[i].SetNumber(0) for i in range(8)],
            c.SetDeaths(c.CurrentPlayer, c.SetTo, ut.b2i4(b"0000"), 0),
        ]
    )

    def f(x):
        t = x % 16
        q, r = divmod(t, 4)
        return 2 ** (r + 8 * (3 - q))

    for i in range(31, -1, -1):
        c.RawTrigger(
            conditions=number.AtLeast(2 ** i),
            actions=[
                number.SubtractNumber(2 ** i),
                digit[i // 4].AddNumber(2 ** (i % 4)),
                c.SetDeaths(c.CurrentPlayer, c.Add, f(i), 0),
            ],
        )
        if i % 16 == 0:
            for j in range(4):
                c.RawTrigger(
                    conditions=digit[j + 4 * (i // 16)].AtLeast(10),
                    actions=c.SetDeaths(
                        c.CurrentPlayer,
                        c.Add,
                        (b"A"[0] - b":"[0]) * (256 ** (3 - j)),
                        0,
                    ),
                )
            cs.DoActions(
                [
                    c.AddCurrentPlayer(1),
                    [
                        c.SetDeaths(c.CurrentPlayer, c.SetTo, ut.b2i4(b"0000"), 0)
                        if i == 16
                        else []
                    ],
                ]
            )


def f_cpstr_print(*args, EOS=True, encoding="UTF-8"):
    """Print multiple string / number to CurrentPlayer.

    :param args: Things to print

    """
    args = ut.FlattenList(args)
    for arg in args:
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
        elif ut.isUnproxyInstance(arg, c.EUDVariable) or c.IsConstExpr(arg):
            f_cpstr_adddw(arg)
        elif ut.isUnproxyInstance(arg, hptr):
            f_cpstr_addptr(arg._value)
        else:
            raise ut.EPError(
                "Object with unknown parameter type %s given to f_cpprint." % type(arg)
            )
    if EOS:
        cs.DoActions(c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0))


@c.EUDTypedFunc([c.TrgPlayer])
def f_raise_CCMU(player):
    if cs.EUDIf()(c.Memory(0x628438, c.AtLeast, 0x59CCA8)):
        orignextptr = f_cunitread_epd(ut.EPD(0x628438))
        print_error = c.Forward()
        c.VProc(player, player.SetDest(ut.EPD(print_error + 16)))
        c.VProc(orignextptr, [
            c.SetMemory(0x628438, c.SetTo, 0),
            print_error << c.CreateUnit(1, 0, 64, 0),
            orignextptr.SetDest(ut.EPD(0x628438)),
        ])
    if cs.EUDElse()():
        cs.DoActions(c.CreateUnit(1, 0, 64, player))
    cs.EUDEndIf()


_eprintln_template = None
_eprintln_print = c.Forward()
_eprintln_EOS = c.Forward()
_eprintln_end = c.Forward()


def f_eprintln(*args, encoding="UTF-8"):
    global _eprintln_template
    if _eprintln_template is None:
        _eprintln_template = c.Forward()

        c.PushTriggerScope()
        _eprintln_template << c.NextTrigger()
        f_raise_CCMU(c.CurrentPlayer)
        if cs.EUDIf()(c.Memory(0x512684, c.Exactly, prevcp)):
            _eprintln_print << c.RawTrigger(
                nextptr=0, actions=[c.SetCurrentPlayer(ut.EPD(0x640B60 + 218 * 12))]
            )
            _eprintln_EOS << c.RawTrigger(
                actions=[c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0)]
            )
            f_setcurpl(prevcp)
        cs.EUDEndIf()
        _eprintln_end << c.RawTrigger(nextptr=0)
        c.PopTriggerScope()

    _print, _next = c.Forward(), c.Forward()
    prevcp << f_getcurpl()
    c.RawTrigger(
        nextptr=_eprintln_template,
        actions=[
            c.SetNextPtr(_eprintln_print, _print),
            c.SetNextPtr(_eprintln_end, _next),
        ],
    )
    _print << c.NextTrigger()
    f_cpstr_print(*args, EOS=False, encoding=encoding)
    c.SetNextTrigger(_eprintln_EOS)
    _next << c.NextTrigger()


_eprintln2_template = None
_eprintln2_print = c.Forward()
_eprintln2_EOS = c.Forward()
_eprintln2_end = c.Forward()


def f_eprintln2(*args, encoding="cp949"):
    global _eprintln2_template
    if _eprintln2_template is None:
        _eprintln2_template = c.Forward()

        c.PushTriggerScope()
        _eprintln2_template << c.NextTrigger()

        if cs.EUDExecuteOnce()():
            # [871] Unit's waypoint list is full.
            ptr = GetTBLAddr(871)
            f_dwwrite(ptr, ut.b2i4(b"\r\r\r\r"))
            epd = ut.EPD(ptr) + 1
        cs.EUDEndExecuteOnce()

        if cs.EUDIf()(c.Memory(0x512684, c.Exactly, prevcp)):
            f_setcurpl(epd)
            _eprintln2_print << c.RawTrigger(nextptr=0)
            _eprintln2_EOS << c.RawTrigger(
                actions=[c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, 0)]
            )
            f_setcurpl(prevcp)
        cs.EUDEndIf()
        _eprintln2_end << c.RawTrigger(nextptr=0)
        c.PopTriggerScope()

    _print, _next = c.Forward(), c.Forward()
    prevcp << f_getcurpl()
    c.RawTrigger(
        nextptr=_eprintln2_template,
        actions=[
            c.SetNextPtr(_eprintln2_print, _print),
            c.SetNextPtr(_eprintln2_end, _next),
        ],
    )
    _print << c.NextTrigger()
    f_cpstr_print(*args, EOS=False, encoding=encoding)
    c.SetNextTrigger(_eprintln2_EOS)
    _next << c.NextTrigger()
