#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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

from ..memiof import EUDByteReader

_global_parser = None


class _EUDParser(EUDByteReader):
    def __init__(self):
        super().__init__()
        self._number, self._digits = c.EUDCreateVariables(2)

    def _trim(self, b):
        lastblock = ut.EUDGetLastBlock()[1]
        cont, end = c.Forward(), c.Forward()

        trim = c.RawTrigger(actions=c.SetNextPtr(cont, end))
        for whitespace in " \t\n\f\r":
            c.RawTrigger(
                conditions=[b == ord(whitespace)],
                actions=self._digits.SetNumber(1 << 31),
            )
        cont << c.RawTrigger(
            conditions=[self._digits == 1 << 31],
            actions=[
                self._digits.SetNumber(0),
                c.SetNextPtr(cont, lastblock["loopstart"]),
            ],
        )
        end << c.NextTrigger()
        return trim

    def _sign(self, b, jumper):
        lastblock = ut.EUDGetLastBlock()[1]
        cont, end = c.Forward(), c.Forward()

        cs.DoActions([c.SetNextPtr(jumper, end), c.SetNextPtr(cont, end)])
        c.RawTrigger(
            conditions=[b == ord("-")],
            actions=[
                self._digits.SetNumber(1 << 31),
                c.SetNextPtr(cont, lastblock["loopstart"]),
            ],
        )
        cont << c.RawTrigger(
            conditions=[b == ord("+")],
            actions=c.SetNextPtr(cont, lastblock["loopstart"]),
        )
        end << c.NextTrigger()

    @c.EUDMethod
    def _parse_dw(self):
        # \s*[+-]?\d+
        jumper, trim = c.Forward(), c.Forward()
        cs.DoActions(
            [
                self._number.SetNumber(0),
                self._digits.SetNumber(0),
                c.SetNextPtr(jumper, trim),
            ]
        )
        if cs.EUDInfLoop()():
            block = ut.EUDPeekBlock("infloopblock")[1]

            b = self.readbyte()
            jumper << c.RawTrigger()

            # Skip white space and pick up leading +/- sign if any.
            trim << self._trim(b)
            self._sign(b, jumper)

            # \d+
            is_digit = c.Forward()
            is_digit << c.RawTrigger(
                conditions=[b >= ord("0"), b <= ord("9")],
                actions=[
                    b.SubtractNumber(ord("0")),
                    c.SetNextPtr(is_digit, block["contpoint"]),
                ],
            )
            fin = c.NextTrigger()
            cs.EUDBreak()

            cs.EUDSetContinuePoint()
            # TODO: handle overflow
            self._number *= 10
            c.SeqCompute(
                [
                    (ut.EPD(is_digit) + 1, c.SetTo, fin),
                    (self._digits, c.Add, 1),
                    (self._number, c.Add, b),
                ]
            )
            # ignore leading zeros
            c.RawTrigger(
                conditions=[self._number == 0],
                actions=self._digits.SetNumberX(1, (1 << 31) - 1),
            )
        cs.EUDEndInfLoop()

        if cs.EUDIf()(self._digits.AtLeastX(1, 1 << 31)):
            self._number << -self._number
        cs.EUDEndIf()
        cs.DoActions(self._digits.SetNumberX(0, 1 << 31))

        c.EUDReturn(self._number, self._digits)

    @c.EUDMethod
    def _parse_from_radix(self, radix):
        # \s*[+-]?(0[bB])?[01]+
        jumper, trim = c.Forward(), c.Forward()
        cs.DoActions(
            [
                self._number.SetNumber(0),
                self._digits.SetNumber(0),
                c.SetNextPtr(jumper, trim),
            ]
        )
        if cs.EUDInfLoop()():
            block = ut.EUDPeekBlock("infloopblock")[1]

            b = self.readbyte()
            jumper << c.RawTrigger()

            # Skip white space and pick up leading +/- sign if any.
            trim << self._trim(b)
            self._sign(b, jumper)

            # (0[bB])?
            is_zero, is_literal = c.Forward(), c.Forward()
            assume_decimal, cont, is_alphanumeric = [c.Forward() for _ in range(3)]

            cs.DoActions(
                [
                    c.SetNextPtr(is_zero, assume_decimal),
                    c.SetNextPtr(cont, is_alphanumeric),
                ]
            )
            is_zero << c.RawTrigger(
                nextptr=0,
                conditions=[b == ord("0")],
                actions=[
                    self._digits.AddNumber(1),
                    c.SetNextPtr(jumper, is_literal),
                    c.SetNextPtr(is_zero, block["loopstart"]),
                ],
            )
            # if there is a leading zero, check for binary literal
            is_literal << c.NextTrigger()
            for literal, base in zip("bBoOxX", (2, 2, 8, 8, 16, 16)):
                c.RawTrigger(
                    conditions=[b == ord(literal), radix == base],
                    actions=c.SetNextPtr(cont, block["loopstart"]),
                )
                c.RawTrigger(
                    conditions=[b == ord(literal), radix == 0],
                    actions=[
                        c.SetNextPtr(cont, block["loopstart"]),
                        radix.SetNumber(base),
                    ],
                )
            assume_decimal << c.RawTrigger(
                conditions=[radix == 0], actions=radix.SetNumber(10)
            )
            cont << c.RawTrigger(
                nextptr=0, actions=c.SetNextPtr(jumper, is_alphanumeric)
            )

            # [\da-zA-Z]+
            fin = c.Forward()
            is_alphanumeric << c.RawTrigger(actions=c.SetNextPtr(fin, block["loopend"]))
            c.RawTrigger(
                conditions=[b >= ord("0"), b <= ord("9")],
                actions=[
                    b.SubtractNumber(ord("0")),
                    c.SetNextPtr(fin, block["contpoint"]),
                ],
            )
            c.RawTrigger(
                conditions=[b >= ord("a"), b <= ord("z")],
                actions=[
                    b.SubtractNumber(ord("a") - 10),
                    c.SetNextPtr(fin, block["contpoint"]),
                ],
            )
            c.RawTrigger(
                conditions=[b >= ord("A"), b <= ord("Z")],
                actions=[
                    b.SubtractNumber(ord("A") - 10),
                    c.SetNextPtr(fin, block["contpoint"]),
                ],
            )
            fin << c.RawTrigger(nextptr=0)

            cs.EUDSetContinuePoint()
            cs.EUDBreakIf(b >= radix)
            # TODO: handle overflow
            self._number *= radix
            c.SeqCompute([(self._digits, c.Add, 1), (self._number, c.Add, b)])
            # ignore leading zeros
            c.RawTrigger(
                conditions=[self._number == 0],
                actions=self._digits.SetNumberX(1, (1 << 31) - 1),
            )
        cs.EUDEndInfLoop()

        if cs.EUDIf()(self._digits.AtLeastX(1, 1 << 31)):
            self._number << -self._number
        cs.EUDEndIf()
        cs.DoActions(self._digits.SetNumberX(0, 1 << 31))

        c.EUDReturn(self._number, self._digits)


def _GetGlobalEUDParser():
    global _global_parser
    if _global_parser is None:
        _global_parser = _EUDParser()
    return _global_parser


def f_parse(dst, radix=10):
    if radix in (int, 10):
        return _parse_dw(dst)
    else:
        return _parse_from_radix(dst, radix)


@c.EUDFunc
def _parse_dw(dst):
    global_parser = _GetGlobalEUDParser()
    global_parser.seekoffset(dst)
    number, digits = global_parser._parse_dw()
    c.EUDReturn(number, digits)


@c.EUDFunc
def _parse_from_radix(dst, radix):
    global_parser = _GetGlobalEUDParser()
    global_parser.seekoffset(dst)
    if cs.EUDIf()(radix == 10):
        number, digits = global_parser._parse_dw()
        c.EUDReturn(number, digits)
    cs.EUDEndIf()
    number, digits = global_parser._parse_from_radix(radix)
    c.EUDReturn(number, digits)
