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

from ..rwcommon import br1, bw1
from .dbstr import DBString


@c.EUDFunc
def f_dbstr_addstr(dst, src):
    """Print string as string to dst. Same as strcpy except of return value.

    :param dst: Destination address (Not EPD player)
    :param src: Source address (Not EPD player)

    :returns: dst + strlen(src)
    """
    b = c.EUDVariable()

    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if cs.EUDInfLoop()():
        c.SetVariables(b, br1.readbyte())
        bw1.writebyte(b)
        cs.EUDBreakIf(b == 0)
        dst += 1
    cs.EUDEndInfLoop()

    return dst


@c.EUDFunc
def f_dbstr_adddw(dst, number):
    """Print number as string to dst.

    :param dst: Destination address (Not EPD player)
    :param number: DWORD to print

    :returns: dst + strlen(itoa(number))
    """
    bw1.seekoffset(dst)

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
        bw1.writebyte(ch[i] + b"0"[0])
        dst += 1

    bw1.writebyte(0)  # EOS

    return dst


@c.EUDFunc
def f_dbstr_addptr(dst, number):
    """Print number as string to dst.

    :param dst: Destination address (Not EPD player)
    :param number: DWORD to print

    :returns: dst + strlen(itoa(number))
    """
    bw1.seekoffset(dst)
    ch = [0] * 8

    # Get digits
    for i in range(8):
        number, ch[i] = c.f_div(number, 16)

    # print digits
    for i in range(7, -1, -1):
        if cs.EUDIf()(ch[i] <= 9):
            bw1.writebyte(ch[i] + b"0"[0])
        if cs.EUDElse()():
            bw1.writebyte(ch[i] + (b"A"[0] - 10))
        cs.EUDEndIf()
        dst += 1

    bw1.writebyte(0)  # EOS

    return dst


class ptr2s:
    def __init__(self, value):
        self._value = value


class epd2s:
    def __init__(self, value):
        self._value = value


class hptr:
    def __init__(self, value):
        self._value = value


def f_dbstr_print(dst, *args, encoding="UTF-8"):
    """Print multiple string / number to dst.

    :param dst: Destination address (Not EPD player)
    :param args: Things to print

    """
    if ut.isUnproxyInstance(dst, DBString):
        dst = dst.GetStringMemoryAddr()

    args = ut.FlattenList(args)
    for arg in args:
        if ut.isUnproxyInstance(arg, bytes):
            dst = f_dbstr_addstr(dst, c.Db(arg + b"\0"))
        elif ut.isUnproxyInstance(arg, str):
            dst = f_dbstr_addstr(dst, c.Db(arg.encode(encoding) + b"\0"))
        elif ut.isUnproxyInstance(arg, DBString):
            dst = f_dbstr_addstr(dst, arg.GetStringMemoryAddr())
        elif ut.isUnproxyInstance(arg, ptr2s):
            dst = f_dbstr_addstr(dst, arg._value)
        elif ut.isUnproxyInstance(arg, int):
            # int and c.EUDVariable should act the same if possible.
            # EUDVariable has a value of 32bit unsigned integer.
            # So we adjust arg to be in the same range.
            dst = f_dbstr_addstr(dst, c.Db(str(arg & 0xFFFFFFFF)))
        elif ut.isUnproxyInstance(arg, c.EUDVariable):
            dst = f_dbstr_adddw(dst, arg)
        elif c.IsConstExpr(arg):
            dst = f_dbstr_adddw(dst, arg)
        elif ut.isUnproxyInstance(arg, hptr):
            dst = f_dbstr_addptr(dst, arg._value)
        else:
            raise ut.EPError(
                "Object wit unknown parameter type %s given to f_eudprint." % type(arg)
            )

    return dst


_printf_buffer = DBString(8192)


def f_simpleprint(*args, spaced=True):
    # Add spaces between arguments
    if spaced:
        spaced_args = []
        for arg in args:
            spaced_args.extend([arg, " "])
        args = spaced_args[:-1]

    # Print
    f_dbstr_print(_printf_buffer, *args)
    _printf_buffer.Display()
