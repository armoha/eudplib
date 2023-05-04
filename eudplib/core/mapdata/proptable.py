#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from eudplib import utils as ut
from eudplib.localize import _

from .chktok import CHK
from .unitprp import PropertyKey, UnitProperty

_uprpdict: dict[bytes, int] = {}
_uprptable: list[bytes] = []


def InitPropertyMap(chkt: "CHK") -> None:
    global _prptable, _uprpdict
    _uprpdict.clear()
    _uprptable.clear()
    _uprptable.extend([b""] * 64)

    # Backup UPRP data
    uprp = chkt.getsection("UPRP")
    try:
        upus = chkt.getsection("UPUS")
    except KeyError:
        upus = bytes([1] * 64)

    for i in range(64):
        if upus[i]:
            uprpdata = PropertyKey(uprp, 20 * i)
            # FIXME: merge duplicates and fix existing CUWPs
            _uprpdict[uprpdata] = i
            _uprptable[i] = uprpdata


def GetPropertyIndex(prop: UnitProperty | bytes) -> int:
    ut.ep_assert(
        isinstance(prop, UnitProperty) or isinstance(prop, bytes),
        _("Invalid property type"),
    )

    prop = PropertyKey(bytes(prop))
    try:
        return _uprpdict[prop] + 1  # SC counts unit properties from 1.

    except KeyError:
        indexNotFound = False
        for uprpindex in range(64):
            if not _uprptable[uprpindex]:
                indexFound = True
                break

        ut.ep_assert(indexFound, _("Unit property table overflow"))

        _uprptable[uprpindex] = prop
        _uprpdict[prop] = uprpindex
        return uprpindex + 1  # SC counts unit properties from 1.


def ApplyPropertyMap(chkt: "CHK") -> None:
    uprpdata = b"".join([uprpdata or bytes(20) for uprpdata in _uprptable])
    chkt.setsection("UPRP", uprpdata)
