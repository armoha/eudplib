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

from ...localize import _
from ...utils import ep_warn


def FixMapData(chkt):
    FixUnitMap(chkt)
    FixSettings(chkt)
    ApplyRemasteredChk(chkt)
    RemoveLocationStringInfo(chkt)
    FixMTXM0_0Null(chkt)


def FixUnitMap(chkt):
    unit = bytearray(chkt.getsection("UNIT"))

    for i in range(0, len(unit), 36):
        # Disable flags for default value
        if unit[i + 17] == 100:
            unit[i + 14] &= ~2
        if unit[i + 18] == 100:
            unit[i + 14] &= ~4
        if unit[i + 24 : i + 26] == b"\0\0":
            unit[i + 14] &= ~32
        for k in range(5):
            if unit[i + 26] & (2 ** k) == 0:
                unit[i + 12] &= ~(2 ** k)

        # Remove disabled values
        # if unit[i + 14] & 1 == 0:
        #     unit[i + 16] = 0
        if unit[i + 14] & 2 == 0:
            unit[i + 17] = 0
        if unit[i + 14] & 4 == 0:
            unit[i + 18] = 0
        if unit[i + 14] & 8 == 0:
            unit[i + 19] = 0
        if unit[i + 14] & 16 == 0:
            unit[i + 20 : i + 24] = b"\0\0\0\0"
        if unit[i + 14] & 32 == 0:
            unit[i + 24 : i + 26] = b"\0\0"
        for k in range(5):
            if unit[i + 12] & (2 ** k) == 0:
                unit[i + 26] &= ~(2 ** k)

    chkt.setsection("UNIT", unit)


def FixSettings(chkt):
    sections = (
        ("UNIx", 228, (4, 2, 1, 2, 2, 2, 2)),
        ("UPGx", 61, (2, 2, 2, 2, 2, 2)),
        ("TECx", 44, (2, 2, 2, 2)),
    )
    for name, count, settings in sections:
        data = bytearray(chkt.getsection(name))

        for i in range(count):
            if data[i] == 0:
                continue
            offset = count
            if name == "UPGx":
                offset += 1
            for setting in settings:
                for k in range(setting):
                    data[offset + setting * i + k] = 0
                offset += setting * count

        chkt.setsection(name, data)


def ApplyRemasteredChk(chkt):
    chkt.setsection("VER ", b"\xCE\0")


def RemoveLocationStringInfo(chkt):
    mrgn = bytearray(chkt.getsection("MRGN"))

    for i in range(0, len(mrgn), 20):
        mrgn[i + 16 : i + 18] = b"\0\0"

    chkt.setsection("MRGN", mrgn)


def FixMTXM0_0Null(chkt):
    mtxm = bytearray(chkt.getsection("MTXM"))

    hasNull = False
    for i in range(0, len(mtxm), 2):
        if mtxm[i : i + 2] == b"\0\0":
            mtxm[i : i + 2] = b"\x01\0"
            hasNull = True

    if hasNull:
        ep_warn(_("[Warning] Input map has [0, 0] null tiles."))
        print(_("Overwrited them to [0, 1], because they cause desync."))

    chkt.setsection("MTXM", mtxm)
