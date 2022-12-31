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

from ...localize import _
from ...utils import EPError, b2i2, b2i4, ep_assert, ep_warn, u2b, u2utf8, unProxy
from .chktok import CHK
from .tblformat import TBL


class StringIdMap:
    def __init__(self) -> None:
        self._s2id: dict[bytes, int] = {}

    def AddItem(self, string: str | bytes, strid: int) -> None:
        byte = u2b(unProxy(string))
        if byte in self._s2id:  # ambiguous string
            # self._s2id[string] = None
            ep_warn(_("Ambiguous string {}").format(string))
        else:
            self._s2id[byte] = strid

    def GetStringIndex(self, string: str | bytes) -> int:
        byte = u2utf8(unProxy(string))
        if byte not in self._s2id:
            byte = u2b(unProxy(string))
        retid = self._s2id[byte]
        return retid


strmap: TBL | None = None
strsection: str | None = None
unitmap: StringIdMap | None = None
locmap: StringIdMap | None = None
swmap: StringIdMap | None = None


def InitStringMap(chkt: CHK) -> None:
    global strmap, strsection, unitmap, locmap, swmap

    unitmap = StringIdMap()
    locmap = StringIdMap()
    swmap = StringIdMap()
    init_chkt = [chkt, unitmap, locmap, swmap]

    try:
        strx = chkt.getsection("STRx")
    except KeyError:
        pass
    else:
        strsection = "STRx"
        strmap = TBL(strx, init_chkt, load_entry=4, save_entry=4)
        return
    strsection = "STRx"
    strmap = TBL(chkt.getsection("STR"), init_chkt, save_entry=4)


def GetLocationIndex(l: str | bytes) -> int:
    if locmap is None:
        raise EPError(_("Must use LoadMap first"))
    return locmap.GetStringIndex(l) + 1


def GetStringIndex(s: str | bytes) -> int:
    if strmap is None:
        raise EPError(_("Must use LoadMap first"))
    return strmap.GetStringIndex(s)


def GetSwitchIndex(s: str | bytes) -> int:
    if swmap is None:
        raise EPError(_("Must use LoadMap first"))
    return swmap.GetStringIndex(s)


def GetUnitIndex(u: str | bytes) -> int:
    if unitmap is None:
        raise EPError(_("Must use LoadMap first"))
    return unitmap.GetStringIndex(u)


def ApplyStringMap(chkt: CHK) -> None:
    if strmap is None:
        raise EPError(_("Must use LoadMap first"))
    chkt.setsection(strsection, strmap.SaveTBL())


def ForceAddString(s: str | bytes) -> int:
    if strmap is None:
        raise EPError(_("Must use LoadMap first"))
    return strmap.ForceAddString(s) + 1


def GetStringMap() -> TBL | None:
    return strmap


def GetStringSectionName() -> str | None:
    return strsection
