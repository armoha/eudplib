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

from ..mapdata import GetLocationIndex, GetStringIndex, GetSwitchIndex, GetUnitIndex

from eudplib import utils as ut
from eudplib.localize import _

from .strdict import (
    DefAIScriptDict,
    DefLocationDict,
    DefSwitchDict,
    DefUnitDict,
    DefTBLDict,
)

import difflib


def EncodeAIScript(ais, issueError=False):
    ais = ut.unProxy(ais)

    if isinstance(ais, str):
        ais = ut.u2b(ais)

    if isinstance(ais, bytes):
        ut.ep_assert(len(ais) >= 4, _("AIScript name too short"))

        if len(ais) > 4:
            return ut.b2i4(DefAIScriptDict[ais])

        elif len(ais) == 4:
            return ut.b2i4(ais)

    return ais


def _EncodeAny(t, f, dl, s, issueError, *, dlo=0):
    s = ut.unProxy(s)

    if isinstance(s, str) or isinstance(s, bytes):
        try:
            return f(s)
        except KeyError:
            if isinstance(s, str):
                try:
                    ret = dl[s]
                    if dlo:
                        ret += dlo
                    return ret
                except KeyError:
                    sl = _("Cannot encode string {} as {}.").format(s, t)
                    for match in difflib.get_close_matches(s, dl.keys()):
                        sl += "\n" + _(" - Suggestion: {}").format(match)
                    raise ut.EPError(sl)

            if issueError:
                raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))
            return s

    try:
        return dl.get(s, s)

    except TypeError:  # unhashable
        return s


def EncodeLocation(loc, issueError=False):
    return _EncodeAny("location", GetLocationIndex, DefLocationDict, loc, issueError)


def EncodeString(s, issueError=False):
    return _EncodeAny("CHKString", GetStringIndex, {}, s, issueError)


def EncodeSwitch(sw, issueError=False):
    return _EncodeAny("switch", GetSwitchIndex, DefSwitchDict, sw, issueError)


def EncodeUnit(u, issueError=False):
    return _EncodeAny("unit", GetUnitIndex, DefUnitDict, u, issueError)


def EncodeTBL(t, issueError=False):
    s = ut.unProxy(t)

    if isinstance(s, str):
        try:
            return DefTBLDict[s]
        except KeyError:
            sl = _("Cannot encode string {} as {}.").format(s, "stat_txt.tbl")
            for match in difflib.get_close_matches(s, DefTBLDict.keys()):
                sl += "\n" + _(" - Suggestion: {}").format(match)
            raise ut.EPError(sl)
        if issueError:
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(t, "stat_txt.tbl"))
        return s

    try:
        return DefTBLDict.get(s, s)

    except TypeError:  # unhashable
        return s
