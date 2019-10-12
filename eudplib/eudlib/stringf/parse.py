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

from ..rwcommon import br1


def f_parse(dst, radix=10):
    parse_funcs = {
        bin: _parse_bin,
        int: _parse_dw,
        hex: _parse_ptr,
        2: _parse_bin,
        10: _parse_dw,
        16: _parse_ptr,
    }
    try:
        return parse_funcs[radix](dst)
    except KeyError:
        if c.IsEUDVariable(radix):
            return _parse_from_radix(dst, radix)
        raise EPError("Unsupported radix: {}".format(radix))


@c.EUDFunc
def _parse_from_radix(dst, radix):
    if cs.EUDIf()(radix == 2):
        c.EUDReturn(_parse_bin(dst))
    if cs.EUDElseIf()(radix == 16):
        c.EUDReturn(_parse_ptr(dst))
    cs.EUDEndIf()
    c.EUDReturn(_parse_dw(dst))


@c.EUDFunc
def _parse_bin(dst):
    # -?(0b)?[01]+ ≈ [-0b]*[01]+
    ret, neg = c.EUDVariable(), c.EUDLightVariable()
    cs.DoActions([ret.SetNumber(0), neg.SetNumber(0)])
    br1.seekoffset(dst)

    if cs.EUDWhile()(True):
        start = c.NextTrigger()
        b1 = br1.readbyte()
        if cs.EUDIf()([b1 >= ord("0"), b1 <= ord("1")]):
            b1 -= ord("0")
        if cs.EUDElseIf()(ret == 0):
            if cs.EUDIf()(b1 == ord("-")):
                c.RawTrigger(nextptr=start, actions=neg.AddNumberX(1, 1))
            cs.EUDEndIf()
            cs.EUDContinueIf(b1 == ord("b"))
            cs.EUDBreak()
        if cs.EUDElse()():
            cs.EUDBreak()
        cs.EUDEndIf()
        ret *= 16
        ret += b1
    cs.EUDEndWhile()

    if cs.EUDIf()(neg):
        ret << -ret
    cs.EUDEndIf()

    c.EUDReturn(ret)


@c.EUDFunc
def _parse_dw(dst):
    # -?\d+ ≈ -*\d+
    ret, neg = c.EUDVariable(), c.EUDLightVariable()
    cs.DoActions([ret.SetNumber(0), neg.SetNumber(0)])
    br1.seekoffset(dst)

    if cs.EUDWhile()(True):
        start = c.NextTrigger()
        b1 = br1.readbyte()
        if cs.EUDIf()([ret == 0, b1 == ord("-")]):
            c.RawTrigger(nextptr=start, actions=neg.AddNumberX(1, 1))
        cs.EUDEndIf()
        cs.EUDBreakIfNot([b1 >= ord("0"), b1 <= ord("9")])
        ret *= 10
        c.SeqCompute([(b1, c.Subtract, ord("0")), (ret, c.SetTo, b1)])
    cs.EUDEndWhile()

    if cs.EUDIf()(neg):
        ret << -ret
    cs.EUDEndIf()

    c.EUDReturn(ret)


@c.EUDFunc
def _parse_ptr(dst):
    # -?(0x|0X)?[\dA-Fa-f]+ ≈ [-0xX]*[\dA-Fa-f]+
    ret, neg = c.EUDVariable(), c.EUDLightVariable()
    cs.DoActions([ret.SetNumber(0), neg.SetNumber(0)])
    br1.seekoffset(dst)

    if cs.EUDWhile()(True):
        start = c.NextTrigger()
        b1 = br1.readbyte()
        if cs.EUDIf()([b1 >= ord("0"), b1 <= ord("9")]):
            b1 -= ord("0")
        if cs.EUDElseIf()([b1 >= ord("A"), b1 <= ord("F")]):
            b1 -= ord("A") - 10
        if cs.EUDElseIf()([b1 >= ord("a"), b1 <= ord("f")]):
            b1 -= ord("a") - 10
        if cs.EUDElseIf()(ret == 0):
            if cs.EUDIf()(b1 == ord("-")):
                c.RawTrigger(nextptr=start, actions=neg.AddNumberX(1, 1))
            cs.EUDEndIf()
            cs.EUDContinueIf(b1 == ord("x"))
            cs.EUDContinueIf(b1 == ord("X"))
            cs.EUDBreak()
        if cs.EUDElse()():
            cs.EUDBreak()
        cs.EUDEndIf()
        ret *= 16
        ret += b1
    cs.EUDEndWhile()

    if cs.EUDIf()(neg):
        ret << -ret
    cs.EUDEndIf()

    c.EUDReturn(ret)
