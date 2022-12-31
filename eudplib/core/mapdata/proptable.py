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


from eudplib import utils as ut
from eudplib.localize import _

from .unitprp import UnitProperty

_uprpdict: dict[bytes, int] = {}
_uprptable: list[bytes] = []


def InitPropertyMap(chkt):
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
            uprpdata = uprp[20 * i : 20 * i + 20]
            # TODO: merge duplicates and fix existing CUWPs
            _uprpdict[uprpdata] = i
            _uprptable[i] = uprpdata


def GetPropertyIndex(prop):
    ut.ep_assert(
        isinstance(prop, UnitProperty) or isinstance(prop, bytes),
        _("Invalid property type"),
    )

    prop = bytes(prop)
    try:
        return _uprpdict[prop] + 1  # SC counts unit properties from 1. Sucks

    except KeyError:
        indexNotFound = False
        for uprpindex in range(64):
            if not _uprptable[uprpindex]:
                indexFound = True
                break

        ut.ep_assert(indexFound, _("Unit property table overflow"))

        _uprptable[uprpindex] = prop
        _uprpdict[prop] = uprpindex
        return uprpindex + 1  # SC counts unit properties from 1. Sucks


def ApplyPropertyMap(chkt):
    uprpdata = b"".join([uprpdata or bytes(20) for uprpdata in _uprptable])
    chkt.setsection("UPRP", uprpdata)
