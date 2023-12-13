#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from ...localize import _
from ...utils import EPError, u2b, u2utf8, unProxy
from .chktok import CHK
from .tblformat import TBL


class StringIdMap:
    def __init__(self) -> None:
        self._s2id: dict[bytes, int | None] = {}

    def add_item(self, string: str | bytes, strid: int) -> None:
        byte = u2b(unProxy(string))
        if byte in self._s2id:  # ambiguous string
            self._s2id[byte] = None
        else:
            self._s2id[byte] = strid

    def GetStringIndex(self, string: str | bytes) -> int:  # noqa: N802
        byte = u2utf8(unProxy(string))
        if byte not in self._s2id:
            byte = u2b(unProxy(string))
        if byte not in self._s2id:
            raise KeyError(string)
        retid = self._s2id.get(byte)
        if retid is None:
            raise KeyError(
                _(
                    "Ambiguous string; multiple entries have duplicated contents: {}"
                ).format(string)
            )
        return retid


strmap: TBL | None = None
strsection: str | None = None
unitmap: StringIdMap | None = None
locmap: StringIdMap | None = None
swmap: StringIdMap | None = None


def init_stringmaps(chkt: CHK) -> None:
    global strmap, strsection, unitmap, locmap, swmap

    unitmap = StringIdMap()
    locmap = StringIdMap()
    swmap = StringIdMap()
    init_chkt = (chkt, unitmap, locmap, swmap)

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


def GetLocationIndex(loc: str | bytes) -> int:  # noqa: N802
    if locmap is None:
        raise EPError(_("Must use LoadMap first"))
    return locmap.GetStringIndex(loc) + 1


def GetStringIndex(s: str | bytes) -> int:  # noqa: N802
    if strmap is None:
        raise EPError(_("Must use LoadMap first"))
    return strmap.GetStringIndex(s)


def GetSwitchIndex(s: str | bytes) -> int:  # noqa: N802
    if swmap is None:
        raise EPError(_("Must use LoadMap first"))
    return swmap.GetStringIndex(s)


def GetUnitIndex(u: str | bytes) -> int:  # noqa: N802
    if unitmap is None:
        raise EPError(_("Must use LoadMap first"))
    return unitmap.GetStringIndex(u)


def apply_string_map(chkt: CHK) -> None:
    if strsection is None or strmap is None:
        raise EPError(_("Must use LoadMap first"))
    chkt.setsection(strsection, strmap.save_tbl())


def ForceAddString(s: str | bytes) -> int:  # noqa: N802
    if strmap is None:
        raise EPError(_("Must use LoadMap first"))
    return strmap.ForceAddString(s) + 1


def get_string_map() -> TBL:
    if strmap is None:
        raise EPError(_("Must use LoadMap first"))
    return strmap


def get_string_section_name() -> str:
    if strsection is None:
        raise EPError(_("Must use LoadMap first"))
    return strsection
