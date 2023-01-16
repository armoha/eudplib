#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

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
_listfiles: list[tuple[str, bytes | None]] = []


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


def IterListFiles() -> Iterator[tuple[str, bytes | None]]:
    for n, f in _listfiles:
        yield n, f
