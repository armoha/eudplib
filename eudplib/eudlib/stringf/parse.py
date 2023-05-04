#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from eudplib import core as c
from eudplib import ctrlstru as cs
from eudplib import utils as ut

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

        cs.DoActions(c.SetNextPtr(jumper, end), c.SetNextPtr(cont, end))
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
        number, digits = self._number, self._digits
        cs.DoActions(number.SetNumber(0), digits.SetNumber(0), c.SetNextPtr(jumper, trim))
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
            # handle overflow
            cutoff, cutlim = divmod(0x7FFFFFFF, 10)
            c.RawTrigger(
                conditions=[
                    number == cutoff,
                    digits.AtLeastX(cutlim + 1, (1 << 31) - 1),
                ],
                actions=digits.SetNumberX(1 << 30, 1 << 30),
            )
            c.RawTrigger(
                conditions=[number >= cutoff + 1],
                actions=digits.SetNumberX(1 << 30, 1 << 30),
            )

            number *= 10
            # ignore leading zeros
            c.RawTrigger(conditions=[number == 0], actions=digits.SetNumberX(0, (1 << 30) - 1))
            c.SeqCompute(
                [
                    (ut.EPD(is_digit) + 1, c.SetTo, fin),
                    (digits, c.Add, 1),
                    (number, c.Add, b),
                ]
            )
            c.RawTrigger(
                conditions=digits.AtLeastX(11, (1 << 30) - 1),
                actions=digits.SetNumberX(10, (1 << 30) - 1),
            )
        cs.EUDEndInfLoop()

        c.RawTrigger(conditions=digits.AtLeastX(1, 1 << 30), actions=number.SetNumber(0x7FFFFFFF))
        if cs.EUDIf()(digits.AtLeastX(1, 1 << 31)):
            number << -number
        cs.EUDEndIf()
        cs.DoActions(digits.SetNumberX(0, 3 << 30))

        c.EUDReturn(number, digits)

    @c.EUDMethod
    def _parse_from_radix(self, radix):
        # \s*[+-]?(0[bB])?[01]+
        jumper, trim = c.Forward(), c.Forward()
        number, digits = self._number, self._digits
        cs.DoActions(number.SetNumber(0), digits.SetNumber(0), c.SetNextPtr(jumper, trim))
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
                c.SetNextPtr(is_zero, assume_decimal),
                c.SetNextPtr(cont, is_alphanumeric),
            )
            is_zero << c.RawTrigger(
                nextptr=0,
                conditions=[b == ord("0")],
                actions=[
                    digits.AddNumber(1),
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
            assume_decimal << c.RawTrigger(conditions=[radix == 0], actions=radix.SetNumber(10))
            cutoff, cutlim = c.f_div(0xFFFFFFFF, radix)
            cont << c.RawTrigger(
                nextptr=0,
                actions=[c.SetNextPtr(jumper, is_alphanumeric), cutlim.AddNumber(1)],
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

            # handle overflow
            c.RawTrigger(conditions=digits.AtLeastX(1, 1 << 30), actions=digits.AddNumber(-1))
            if cs.EUDIf()([number == cutoff, digits.AtLeastX(cutlim, (1 << 31) - 1)]):
                cs.DoActions(digits.SetNumberX(1 << 30, 1 << 30))
            if cs.EUDElse()():
                cutoff += 1
                if cs.EUDIf()(number >= cutoff):
                    cs.DoActions(digits.SetNumberX(1 << 30, 1 << 30))
                cs.EUDEndIf()
                cutoff -= 1
            cs.EUDEndIf()

            number *= radix
            # ignore leading zeros
            c.RawTrigger(conditions=[number == 0], actions=digits.SetNumberX(0, (1 << 30) - 1))
            c.SeqCompute([(digits, c.Add, 1), (number, c.Add, b)])
        cs.EUDEndInfLoop()

        c.RawTrigger(conditions=digits.AtLeastX(1, 1 << 30), actions=number.SetNumber(0x7FFFFFFF))
        if cs.EUDIf()(digits.AtLeastX(1, 1 << 31)):
            number << -number
        cs.EUDEndIf()
        cs.DoActions(digits.SetNumberX(0, 3 << 30))

        c.EUDReturn(number, digits)


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
