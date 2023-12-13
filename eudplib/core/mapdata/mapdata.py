#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Iterator

from ...localize import _
from ...utils import EPError
from .chktok import CHK
from .playerinfo import init_player_info
from .proptable import apply_property_map, init_property_map
from .stringmap import apply_string_map, init_stringmaps

_inited: bool = False
_chkt: CHK | None = None
_origchkt: CHK | None = None
_rawfile: bytes | None = None
_listfiles: list[tuple[str, bytes | None]] = []


def init_map_data(chkt: CHK, rawfile: bytes) -> None:
    global _inited, _origchkt, _chkt, _rawfile, _listfiles
    _chkt = chkt
    _origchkt = chkt.clone()
    _rawfile = rawfile
    _listfiles = []

    init_stringmaps(chkt)
    init_property_map(chkt)
    init_player_info(chkt)
    _inited = True


def update_map_data() -> None:
    if _chkt is None:
        raise EPError(_("Must use LoadMap first"))
    apply_string_map(_chkt)
    apply_property_map(_chkt)


def AddListFiles(n: str, f: bytes | None) -> None:  # noqa: N802
    _listfiles.append((n, f))


def IsMapdataInitialized() -> bool:  # noqa: N802
    return _inited


def GetChkTokenized() -> CHK:  # noqa: N802
    if _chkt is None:
        raise EPError(_("Must use LoadMap first"))
    return _chkt


def GetOriginalChkTokenized() -> CHK:  # noqa: N802
    """NEVER MODIFY ANYTHING WITHIN THIS CHKTOK"""
    if _origchkt is None:
        raise EPError(_("Must use LoadMap first"))
    return _origchkt


def GetRawFile() -> bytes:  # noqa: N802
    if _rawfile is None:
        raise EPError(_("Must use LoadMap first"))
    return _rawfile


def IterListFiles() -> Iterator[tuple[str, bytes | None]]:  # noqa: N802
    yield from _listfiles
