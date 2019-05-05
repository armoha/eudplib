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

from . import tblformat
from ...utils import b2i2, b2i4, u2b, u2utf8, ep_assert, unProxy


class StringIdMap:
    def __init__(self):
        self._s2id = {}

    def AddItem(self, string, id):
        string = u2b(unProxy(string))
        if string in self._s2id:  # ambiguous string
            self._s2id[string] = None

        else:
            self._s2id[string] = id

    def GetStringIndex(self, string):
        string = u2b(unProxy(string))
        retid = self._s2id[string]
        ep_assert(retid is not None, "Ambigious string %s" % string)
        return retid


strmap = None
unitmap = None
locmap = None
swmap = None


def IgnoreColor(s):
    return bytes(filter(lambda x: not (0x01 <= x <= 0x1F or x == 0x7F), s))


def InitStringMap(chkt):
    global strmap, unitmap, locmap, swmap

    strmap = tblformat.TBL(chkt.getsection("STR"), fix_unitname=True)
    unitmap = StringIdMap()
    locmap = StringIdMap()
    swmap = StringIdMap()

    unix = chkt.getsection("UNIx")
    mrgn = chkt.getsection("MRGN")
    try:
        swnm = chkt.getsection("SWNM")
    except (KeyError):
        swnm = None  # Not Required

    # Get location names
    if mrgn:
        locn = len(mrgn) // 20
        for i in range(locn):
            locstrid = b2i2(mrgn, i * 20 + 16)
            locstr = strmap.GetString(locstrid)
            if locstr:
                locmap.AddItem(locstr, i)

    # Get unit names
    if unix:
        for i in range(228):
            unitstrid = b2i2(unix, 3192 + i * 2)
            unitstr = strmap.GetString(unitstrid)
            if unitstr:
                unitmap.AddItem(unitstr, i)
                if unitstr != IgnoreColor(unitstr):
                    unitmap.AddItem(IgnoreColor(unitstr), i)

    # Get switch names
    if swnm:
        for i in range(256):
            switchstrid = b2i4(swnm, i * 4)
            switchstr = strmap.GetString(switchstrid)
            if switchstr:
                swmap.AddItem(switchstr, i)


def GetLocationIndex(l):
    return locmap.GetStringIndex(l)


def GetStringIndex(s):
    return strmap.GetStringIndex(s)


def GetSwitchIndex(s):
    return swmap.GetStringIndex(s)


def GetUnitIndex(u):
    return unitmap.GetStringIndex(u2utf8(u))


def ApplyStringMap(chkt):
    chkt.setsection("STR", strmap.SaveTBL())


def ForcedAddString(s):
    return strmap.ForcedAddString(s) + 1


def GetStringMap():
    return strmap
