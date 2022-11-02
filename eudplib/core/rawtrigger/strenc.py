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

import difflib

from eudplib import utils as ut
from eudplib.localize import _

from ..mapdata import GetLocationIndex, GetStringIndex, GetSwitchIndex, GetUnitIndex
from .constenc import _Unique
from .strdict import (
    DefAIScriptDict,
    DefFlingyDict,
    DefIconDict,
    DefImageDict,
    DefIscriptDict,
    DefLocationDict,
    DefPortraitDict,
    DefSpriteDict,
    DefSwitchDict,
    DefTBLDict,
    DefTechDict,
    DefUnitDict,
    DefUnitOrderDict,
    DefUpgradeDict,
    DefWeaponDict,
)


def EncodeAIScript(ais, issueError=False):
    ais = ut.unProxy(ais)

    if isinstance(ais, str):
        ais = ut.u2b(ais)

    if isinstance(ais, bytes):
        ut.ep_assert(len(ais) >= 4, _("AIScript name too short"))

        if len(ais) > 4:
            try:
                return ut.b2i4(DefAIScriptDict[ais])
            except KeyError:
                sl = _("Cannot encode string {} as {}.").format(ais, "AIScript")
                for match in difflib.get_close_matches(ais, DefAIScriptDict.keys()):
                    sl += "\n" + _(" - Suggestion: {}").format(match)
                raise ut.EPError(sl)

        elif len(ais) == 4:
            return ut.b2i4(ais)

    elif isinstance(ais, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(ais, "AIScript"))

    return ais


def _EncodeAny(t, f, dl, s, issueError):
    s = ut.unProxy(s)

    if isinstance(s, str) or isinstance(s, bytes):
        try:
            return f(s)
        except KeyError:
            if isinstance(s, str):
                try:
                    return dl[s]
                except KeyError:
                    sl = _("Cannot encode string {} as {}.").format(s, t)
                    for match in difflib.get_close_matches(s, dl.keys()):
                        sl += "\n" + _(" - Suggestion: {}").format(match)
                    raise ut.EPError(sl)

            if issueError:
                raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))
            return s

    elif isinstance(s, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))

    try:
        return dl.get(s, s)

    except TypeError:  # unhashable
        return s


def EncodeLocation(loc, issueError=False):
    return _EncodeAny("location", GetLocationIndex, DefLocationDict, loc, issueError)


def EncodeString(s, issueError=False):
    return _EncodeAny("MapString", GetStringIndex, {}, s, issueError)


def EncodeSwitch(sw, issueError=False):
    return _EncodeAny("switch", GetSwitchIndex, DefSwitchDict, sw, issueError)


def EncodeUnit(u, issueError=False):
    return _EncodeAny("unit", GetUnitIndex, DefUnitDict, u, issueError)


def EncodeTBL(t, issueError=False):
    # TODO: handle custom stat_txt.tbl
    return _EncodeAny("stat_txt.tbl", lambda s: {}[s], DefTBLDict, t, issueError)


def EncodeFlingy(flingy, issueError=False):
    return _EncodeAny("flingy", lambda s: {}[s], DefFlingyDict, flingy, issueError)


def EncodeIcon(icon, issueError=False):
    return _EncodeAny("icon", lambda s: {}[s], DefIconDict, icon, issueError)


def EncodeSprite(sprite, issueError=False):
    return _EncodeAny("sprite", lambda s: {}[s], DefSpriteDict, sprite, issueError)


def EncodeImage(image, issueError=False):
    return _EncodeAny("image", lambda s: {}[s], DefImageDict, image, issueError)


def EncodeIscript(iscript, issueError=False):
    return _EncodeAny("iscript", lambda s: {}[s], DefIscriptDict, iscript, issueError)


def EncodeUnitOrder(order, issueError=False):
    return _EncodeAny("UnitOrder", lambda s: {}[s], DefUnitOrderDict, order, issueError)


def EncodeWeapon(weapon, issueError=False):
    return _EncodeAny("weapon", lambda s: {}[s], DefWeaponDict, weapon, issueError)


def EncodeTech(tech, issueError=False):
    return _EncodeAny("tech", lambda s: {}[s], DefTechDict, tech, issueError)


def EncodeUpgrade(upgrade, issueError=False):
    return _EncodeAny("upgrade", lambda s: {}[s], DefUpgradeDict, upgrade, issueError)


def EncodePortrait(portrait, issueError=False):
    return _EncodeAny("portrait", lambda s: {}[s], DefPortraitDict, portrait, issueError)
