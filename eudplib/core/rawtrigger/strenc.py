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
from collections.abc import Callable
from typing import TYPE_CHECKING, NoReturn, TypeAlias, overload

from eudplib import utils as ut
from eudplib.localize import _

from ...utils import ExprProxy
from ..mapdata import GetLocationIndex, GetStringIndex, GetSwitchIndex, GetUnitIndex
from .constenc import Byte, Dword, T, Word, _Unique
from .strdict import (
    DefAIScriptDict,
    DefFlingyDict,
    DefIconDict,
    DefImageDict,
    DefIscriptDict,
    DefLocationDict,
    DefPortraitDict,
    DefSpriteDict,
    DefStatTextDict,
    DefSwitchDict,
    DefTechDict,
    DefUnitDict,
    DefUnitOrderDict,
    DefUpgradeDict,
    DefWeaponDict,
)

Unit: TypeAlias = "str | Word | bytes"
Location: TypeAlias = "str | Dword | bytes"
String: TypeAlias = "str | Dword | bytes"
AIScript: TypeAlias = "str | Dword | bytes"
Switch: TypeAlias = "str | Byte | bytes"  # Byte in Condition, Dword in Action

Flingy: TypeAlias = "str | Word | bytes"
Icon: TypeAlias = "str | Word | bytes"
Image: TypeAlias = "str | Word | bytes"
Iscript: TypeAlias = "str | Word | bytes"
Portrait: TypeAlias = "str | Word | bytes"
Sprite: TypeAlias = "str | Word | bytes"
StatText: TypeAlias = "str | Dword | bytes"
Tech: TypeAlias = "str | Word | bytes"
UnitOrder: TypeAlias = "str | Word | bytes"
Upgrade: TypeAlias = "str | Word | bytes"
Weapon: TypeAlias = "str | Word | bytes"


@overload
def EncodeAIScript(ais: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeAIScript(ais: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeAIScript(ais: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeAIScript(ais: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeAIScript(ais, issueError=False):
    ais = ut.unProxy(ais)

    if isinstance(ais, str):
        ais = ut.u2b(ais)

    if isinstance(ais, bytes):
        ut.ep_assert(len(ais) >= 4, _("AIScript name too short"))

        if len(ais) > 4:
            if ais in DefAIScriptDict:
                return ut.b2i4(DefAIScriptDict[ais])
            sl = _("Cannot encode string {} as {}.").format(ais, "AIScript")
            for match in difflib.get_close_matches(ais, DefAIScriptDict.keys()):
                sl += "\n" + _(" - Suggestion: {}").format(match)
            raise ut.EPError(sl)

        elif len(ais) == 4:
            if ais in DefAIScriptDict.values():
                return ut.b2i4(ais)
            sl = _("Cannot encode string {} as {}.").format(ais, "AIScript")
            for match in difflib.get_close_matches(ais, DefAIScriptDict.values()):
                sl += "\n" + _(" - Suggestion: {}").format(match)
            raise ut.EPError(sl)

    elif isinstance(ais, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(ais, "AIScript"))

    return ais


@overload
def _EncodeAny(
    t: str, f: Callable, dl: "dict[str, int]", s: _Unique | ExprProxy[_Unique]
) -> NoReturn:
    ...


@overload
def _EncodeAny(
    t: str, f: Callable, dl: "dict[str, int]", s: str | bytes | ExprProxy[str | bytes]
) -> int:
    ...


@overload
def _EncodeAny(t: str, f: Callable, dl: "dict[str, int]", s: T) -> T:
    ...


@overload
def _EncodeAny(t: str, f: Callable, dl: "dict[str, int]", s: "ExprProxy[T]") -> T:
    ...


def _EncodeAny(t, f, dl, s):
    s = ut.unProxy(s)

    if isinstance(s, str) or isinstance(s, bytes):
        try:
            return f(s)
        except KeyError:
            if isinstance(s, str):
                if s in dl:
                    return dl[s]
                sl = _("Cannot encode string {} as {}.").format(s, t)
                for match in difflib.get_close_matches(s, dl.keys()):
                    sl += "\n" + _(" - Suggestion: {}").format(match)
                raise ut.EPError(sl)
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))

    elif isinstance(s, _Unique):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(s, t))

    try:
        return dl.get(s, s)

    except TypeError:  # unhashable
        return s


@overload
def EncodeLocation(loc: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeLocation(loc: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeLocation(loc: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeLocation(loc: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeLocation(loc, issueError=False):
    return _EncodeAny("location", GetLocationIndex, DefLocationDict, loc)


@overload
def EncodeString(s: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeString(s: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeString(s: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeString(s: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeString(s, issueError=False):
    return _EncodeAny("MapString", GetStringIndex, {}, s)


@overload
def EncodeSwitch(sw: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeSwitch(sw: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeSwitch(sw: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeSwitch(sw: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeSwitch(sw, issueError=False):
    return _EncodeAny("switch", GetSwitchIndex, DefSwitchDict, sw)


@overload
def EncodeUnit(u: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeUnit(u: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeUnit(u: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeUnit(u: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeUnit(u, issueError=False):
    return _EncodeAny("unit", GetUnitIndex, DefUnitDict, u)


@overload
def EncodeTBL(t: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeTBL(t: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeTBL(t: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeTBL(t: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeTBL(t, issueError=False):
    # TODO: handle custom stat_txt.tbl
    return _EncodeAny("stat_txt.tbl", lambda s: {}[s], DefStatTextDict, t)


@overload
def EncodeFlingy(flingy: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeFlingy(flingy: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeFlingy(flingy: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeFlingy(flingy: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeFlingy(flingy, issueError=False):
    return _EncodeAny("flingy", lambda s: {}[s], DefFlingyDict, flingy)


@overload
def EncodeIcon(icon: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeIcon(icon: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeIcon(icon: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeIcon(icon: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeIcon(icon, issueError=False):
    return _EncodeAny("icon", lambda s: {}[s], DefIconDict, icon)


@overload
def EncodeSprite(sprite: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeSprite(sprite: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeSprite(sprite: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeSprite(sprite: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeSprite(sprite, issueError=False):
    return _EncodeAny("sprite", lambda s: {}[s], DefSpriteDict, sprite)


@overload
def EncodeImage(image: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeImage(image: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeImage(image: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeImage(image: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeImage(image, issueError=False):
    return _EncodeAny("image", lambda s: {}[s], DefImageDict, image)


@overload
def EncodeIscript(iscript: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeIscript(iscript: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeIscript(iscript: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeIscript(iscript: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeIscript(iscript, issueError=False):
    return _EncodeAny("iscript", lambda s: {}[s], DefIscriptDict, iscript)


@overload
def EncodeUnitOrder(order: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeUnitOrder(order: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeUnitOrder(order: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeUnitOrder(order: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeUnitOrder(order, issueError=False):
    return _EncodeAny("UnitOrder", lambda s: {}[s], DefUnitOrderDict, order)


@overload
def EncodeWeapon(weapon: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeWeapon(weapon: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeWeapon(weapon: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeWeapon(weapon: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeWeapon(weapon, issueError=False):
    return _EncodeAny("weapon", lambda s: {}[s], DefWeaponDict, weapon)


@overload
def EncodeTech(tech: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeTech(tech: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeTech(tech: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeTech(tech: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeTech(tech, issueError=False):
    return _EncodeAny("tech", lambda s: {}[s], DefTechDict, tech)


@overload
def EncodeUpgrade(upgrade: str | bytes | ExprProxy[str | bytes], issueError: bool = False) -> int:
    ...


@overload
def EncodeUpgrade(upgrade: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodeUpgrade(upgrade: T, issueError: bool = False) -> T:
    ...


@overload
def EncodeUpgrade(upgrade: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodeUpgrade(upgrade, issueError=False):
    return _EncodeAny("upgrade", lambda s: {}[s], DefUpgradeDict, upgrade)


@overload
def EncodePortrait(
    portrait: str | bytes | ExprProxy[str | bytes], issueError: bool = False
) -> int:
    ...


@overload
def EncodePortrait(portrait: _Unique | ExprProxy[_Unique], issueError: bool = False) -> NoReturn:
    ...


@overload
def EncodePortrait(portrait: T, issueError: bool = False) -> T:
    ...


@overload
def EncodePortrait(portrait: "ExprProxy[T]", issueError: bool = False) -> T:
    ...


def EncodePortrait(portrait, issueError=False):
    return _EncodeAny("portrait", lambda s: {}[s], DefPortraitDict, portrait)
