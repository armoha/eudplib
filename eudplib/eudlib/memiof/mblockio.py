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
from ... import utils as ut
from ...core.eudfunc.eudf import _EUDPredefineParam
from . import byterw as bm
from . import cpmemio as cm
from . import modcurpl as cp

_cpmoda = c.Forward()
_cpadda = c.Forward()


@c.EUDFullFunc(
    [(ut.EPD(_cpmoda), c.Add, 0, None), (ut.EPD(0x6509B0), c.SetTo, 0, None)],
    [None, None, None],
)
def f_repmovsd_epd(dstepdp, srcepdp, copydwn):
    global _cpmoda

    c.VProc([dstepdp, srcepdp], c.SetMemory(_cpmoda, c.SetTo, -1))

    if cs.EUDWhileNot()(copydwn == 0):
        cpmod = cm.f_dwread_cp(0)
        _cpmoda << cpmod.getDestAddr()

        c.VProc(
            cpmod,
            [
                cpmod.AddDest(1),
                c.SetMemory(0x6509B0, c.Add, 1),
                copydwn.SubtractNumber(1),
            ],
        )

    cs.EUDEndWhile()

    cp.f_setcurpl2cpcache()


@c.EUDFullFunc(
    [(ut.EPD(_cpadda), c.Add, 0, None), (ut.EPD(0x6509B0), c.SetTo, 0, None)],
    [None, None, None],
)
def _repaddsd_epd(dstepdp, srcepdp, copydwn):
    global _cpadda

    c.VProc(
        [dstepdp, srcepdp],
        [
            c.SetMemory(_cpadda, c.SetTo, -1),
            # TODO: set Add modifier in compile-time
            c.SetMemoryX(_cpadda + 8, c.SetTo, c.EncodeModifier(c.Add) << 24, 0xFF000000),
        ],
    )

    if cs.EUDWhileNot()(copydwn == 0):
        cpadd = cm.f_dwread_cp(0)
        _cpadda << cpadd.getDestAddr()

        c.VProc(
            cpadd,
            [
                cpadd.AddDest(1),
                c.SetMemory(0x6509B0, c.Add, 1),
                copydwn.SubtractNumber(1),
            ],
        )

    cs.EUDEndWhile()

    cp.f_setcurpl2cpcache()


@c.EUDFunc
def _memcpy(dst, src, copylen):
    from ..stringf.rwcommon import br1, bw1

    br1.seekoffset(src)
    bw1.seekoffset(dst)

    if cs.EUDWhile()(copylen >= 1):
        b = br1.readbyte()
        bw1.writebyte(b)
        copylen -= 1
    cs.EUDEndWhile()


def f_memcpy(dst, src, copylen, **kwargs):
    if type(dst) == type(src) == type(copylen) == int and dst % 4 == src % 4 == copylen % 4 == 0:
        return f_repmovsd_epd(ut.EPD(dst), ut.EPD(src), copylen // 4, **kwargs)
    return _memcpy(dst, src, copylen, **kwargs)


@c.EUDFunc
def f_memcmp(buf1, buf2, count):
    from ..stringf.rwcommon import br1, br2

    br1.seekoffset(buf1)
    br2.seekoffset(buf2)

    if cs.EUDWhile()(count >= 1):
        count -= 1
        ch1 = br1.readbyte()
        ch2 = br2.readbyte()
        cs.EUDContinueIf(ch1 == ch2)
        c.EUDReturn(ch1 - ch2)
    cs.EUDEndWhile()

    c.EUDReturn(0)
