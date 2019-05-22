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

from ... import core as c
from ... import ctrlstru as cs
from ...utils import EPD

from .rwcommon import br1, br2, bw1
from ..memiof import f_getcurpl


@c.EUDFunc
def f_strcpy(dst, src):
    """
    Strcpy equivilant in eudplib. Copy C-style string.

    :param dst: Destination address (Not EPD player)
    :param src: Source address (Not EPD player)

    :return: dst
    """
    b = c.EUDVariable()

    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if cs.EUDInfLoop()():
        c.SetVariables(b, br1.readbyte())
        bw1.writebyte(b)
        cs.EUDBreakIf(b == 0)
    cs.EUDEndInfLoop()

    return dst


@c.EUDFunc
def f_strcmp(s1, s2):
    br1.seekoffset(s1)
    br2.seekoffset(s2)

    if cs.EUDInfLoop()():
        ch1 = br1.readbyte()
        ch2 = br2.readbyte()
        if cs.EUDIf()(ch1 == ch2):
            if cs.EUDIf()(ch1 == 0):
                c.EUDReturn(0)
            cs.EUDEndIf()
            cs.EUDContinue()
        if cs.EUDElse()():
            c.EUDReturn(ch1 - ch2)
        cs.EUDEndIf()
    cs.EUDEndInfLoop()


@c.EUDFunc
def f_strlen_epd(epd):
    oldcp = f_getcurpl()
    ret = c.EUDVariable()
    c.VProc(epd, [
        epd.SetDest(EPD(0x6509B0)),
        ret.SetNumber(0),
    ])
    if cs.EUDWhile()(c.Deaths(c.CurrentPlayer, c.AtLeast, 1, 0)):
        cs.EUDBreakIf(c.DeathsX(c.CurrentPlayer, c.Exactly, 0, 0, 0xFF))
        ret += 1
        cs.EUDBreakIf(c.DeathsX(c.CurrentPlayer, c.Exactly, 0, 0, 0xFF00))
        ret += 1
        cs.EUDBreakIf(c.DeathsX(c.CurrentPlayer, c.Exactly, 0, 0, 0xFF0000))
        ret += 1
        cs.EUDBreakIf(c.DeathsX(c.CurrentPlayer, c.Exactly, 0, 0, 0xFF000000))
        cs.DoActions([ret.AddNumber(1), c.SetMemory(0x6509B0, c.Add, 1)])
    cs.EUDEndWhile()
    c.VProc(oldcp, oldcp.SetDest(EPD(0x6509B0)))
    c.EUDReturn(ret)


@c.EUDFunc
def f_strlen(src):
    ret = c.EUDVariable()
    epd, mod = c.f_div(src, 4)
    cs.DoActions([ret.SetNumber(0), epd.AddNumber(-0x58A364 // 4)])
    for i in range(1, 4):
        if cs.EUDIf()(mod == i):
            if cs.EUDIf()(c.MemoryXEPD(epd, c.Exactly, 0, 255 * (256 ** i))):
                c.EUDReturn(ret)
            cs.EUDEndIf()
            cs.DoActions([mod.AddNumber(1), ret.AddNumber(1)])
        cs.EUDEndIf()
    epd += 1
    ret += f_strlen_epd(epd)
    c.EUDReturn(ret)


@c.EUDFunc
def f_strnstr(string, substring, count):
    br1.seekoffset(string)
    br2.seekoffset(substring)
    dst, _offset, _suboffset = c.EUDCreateVariables(3)
    dst << -1

    b = br2.readbyte()
    if cs.EUDIf()(b == 0):
        c.EUDReturn(string)
    cs.EUDEndIf()
    if cs.EUDWhile()(count >= 1):
        a = br1.readbyte()
        cs.DoActions([dst.AddNumber(1), count.SubtractNumber(1)])
        cs.EUDBreakIf(a == 0)
        cs.EUDContinueIfNot(a == b)
        _offset << br1._offset
        _suboffset << br1._suboffset
        if cs.EUDWhile()(1):
            c = br2.readbyte()
            if cs.EUDIf()(c == 0):
                c.EUDReturn(string + dst)
            cs.EUDEndIf()
            cs.EUDBreakIfNot(br1.readbyte() == c)
        cs.EUDEndWhile()
        br1._offset << _offset
        br1._suboffset << _suboffset
        br2.seekoffset(substring + 1)
    cs.EUDEndWhile()
    c.EUDReturn(-1)
