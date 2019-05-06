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


def FixMapData(chkt):
    FixUnitMap(chkt)
    ApplyRemasteredChk(chkt)
    RemoveLocationStringInfo(chkt)


def FixUnitMap(chkt):
    unit = bytearray(chkt.getsection("UNIT"))

    for i in range(0, len(unit), 36):
        if unit[i + 17] == 100:
            unit[i + 14] &= ~2
        if unit[i + 18] == 100:
            unit[i + 14] &= ~4
        if unit[i + 19] == 100:
            unit[i + 14] &= ~8

    chkt.setsection("UNIT", unit)


def ApplyRemasteredChk(chkt):
    chkt.setsection("VER ", b"\xCE\0")


def RemoveLocationStringInfo(chkt):
    mrgn = bytearray(chkt.getsection("MRGN"))

    for i in range(0, len(mrgn), 20):
        mrgn[i + 16:i + 18] = b'\0\0'

    chkt.setsection("MRGN", mrgn)
