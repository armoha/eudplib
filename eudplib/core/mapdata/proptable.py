#!/usr/bin/python
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.


from eudplib import utils as ut
from eudplib.localize import _

from .chktok import CHK
from .unitprp import UnitProperty, property_key

_uprpdict: dict[bytes, int] = {}
_uprptable: list[bytes] = []


def init_property_map(chkt: "CHK") -> None:
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
            uprpdata = property_key(uprp, 20 * i)
            # FIXME: merge duplicates and fix existing CUWPs
            _uprpdict[uprpdata] = i
            _uprptable[i] = uprpdata


def GetPropertyIndex(prop: UnitProperty | bytes) -> int:  # noqa: N802
    ut.ep_assert(
        isinstance(prop, UnitProperty) or isinstance(prop, bytes),
        _("Invalid property type"),
    )

    prop = property_key(bytes(prop))
    try:
        return _uprpdict[prop] + 1  # SC counts unit properties from 1.

    except KeyError:
        index_found = False
        for uprpindex in range(64):
            if not _uprptable[uprpindex]:
                index_found = True
                break

        ut.ep_assert(index_found, _("Unit property table overflow"))

        _uprptable[uprpindex] = prop
        _uprpdict[prop] = uprpindex
        return uprpindex + 1  # SC counts unit properties from 1.


def apply_property_map(chkt: "CHK") -> None:
    uprpdata = b"".join([uprpdata or bytes(20) for uprpdata in _uprptable])
    chkt.setsection("UPRP", uprpdata)
