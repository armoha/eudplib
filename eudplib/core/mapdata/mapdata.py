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

from collections.abc import Iterator

from ...localize import _
from ...utils import EPError
from .chktok import CHK
from .playerinfo import InitPlayerInfo
from .proptable import ApplyPropertyMap, InitPropertyMap
from .stringmap import ApplyStringMap, InitStringMap

_inited: bool = False
_chkt: CHK | None = None
_origchkt: CHK | None = None
_rawfile: bytes | None = None
_listfiles: "list[tuple[str, bytes | None]]" = []


def InitMapData(chkt: CHK, rawfile: bytes) -> None:
    global _inited, _origchkt, _chkt, _rawfile, _listfiles
    _chkt = chkt
    _origchkt = chkt.clone()
    _rawfile = rawfile
    _listfiles = []

    InitStringMap(chkt)
    InitPropertyMap(chkt)
    InitPlayerInfo(chkt)
    _inited = True


def UpdateMapData() -> None:
    if _chkt is None:
        raise EPError(_("Must use LoadMap first"))
    ApplyStringMap(_chkt)
    ApplyPropertyMap(_chkt)


def AddListFiles(n: str, f: bytes | None) -> None:
    _listfiles.append((n, f))


def IsMapdataInitialized() -> bool:
    return _inited


def GetChkTokenized() -> CHK:
    if _chkt is None:
        raise EPError(_("Must use LoadMap first"))
    return _chkt


def GetOriginalChkTokenized() -> CHK:
    """NEVER MODIFY ANYTHING WITHIN THIS CHKTOK"""
    if _origchkt is None:
        raise EPError(_("Must use LoadMap first"))
    return _origchkt


def GetRawFile() -> bytes:
    if _rawfile is None:
        raise EPError(_("Must use LoadMap first"))
    return _rawfile


def IterListFiles() -> "Iterator[tuple[str, bytes | None]]":
    for n, f in _listfiles:
        yield n, f
