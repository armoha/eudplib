# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import difflib
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, TypeAlias, overload

from eudplib import utils as ut
from eudplib.localize import _

from ...utils import ExprProxy
from ..mapdata import (
    GetLocationIndex,
    GetStringIndex,
    GetSwitchIndex,
    GetUnitIndex,
)
from .consttype import Byte, ConstType, Dword, T, U, Word, _Byte, _Dword, _Word
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

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from ..variable import EUDVariable


class TrgAIScript(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeAIScript(s)


class TrgLocation(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeLocation(s)


class TrgString(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeString(s)


class TrgSwitch(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeSwitch(s)


class Iscript(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeIscript(s)


class StatText(ConstType):
    __slots__ = ()
    _encoding = "UTF-8"
    _data = b""

    @classmethod
    def cast(cls, s):
        return EncodeTBL(s)


class Icon(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodeIcon(s)


class Portrait(ConstType):
    __slots__ = ()

    @classmethod
    def cast(cls, s):
        return EncodePortrait(s)


Unit: TypeAlias = "str | Word | bytes"
Location: TypeAlias = "str | Dword | bytes"
String: TypeAlias = "str | Dword | bytes"
AIScript: TypeAlias = "str | Dword | bytes"
Switch: TypeAlias = "str | Byte | bytes"  # Byte in Condition, Dword in Action

_StatText: TypeAlias = "str | Dword | bytes"
_Flingy: TypeAlias = "str | Word | bytes"
_Icon: TypeAlias = "str | Word | bytes"
_Image: TypeAlias = "str | Word | bytes"
_Iscript: TypeAlias = "str | Word | bytes"
_Portrait: TypeAlias = "str | Word | bytes"
_Sprite: TypeAlias = "str | Word | bytes"
_Tech: TypeAlias = "str | Byte | bytes"
_UnitOrder: TypeAlias = "str | Byte | bytes"
_Upgrade: TypeAlias = "str | Byte | bytes"
_Weapon: TypeAlias = "str | Byte | bytes"

# argument types
_ExprProxy: TypeAlias = (
    "ExprProxy[str | bytes | int | EUDVariable | ConstExpr | ExprProxy]"
)
_Arg: TypeAlias = "str | bytes | int | EUDVariable | ConstExpr | ExprProxy[str | bytes | int | EUDVariable | ConstExpr | ExprProxy]"  # noqa: E501
__ExprProxy: TypeAlias = "ExprProxy[str | bytes | int | EUDVariable | ExprProxy]"
__Arg: TypeAlias = "str | bytes | int | EUDVariable | ExprProxy[str | bytes | int | EUDVariable | ExprProxy]"  # noqa: E501


@overload
def EncodeAIScript(ais: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeAIScript(ais: T, issueError: bool = False) -> T:  # noqa: N803
    ...


@overload
def EncodeAIScript(ais: _ExprProxy, issueError: bool = False) -> _Dword:  # noqa: N803
    ...


def EncodeAIScript(ais: _Arg, issueError: bool = False) -> _Dword:  # noqa: N803, N802
    ai = ut.unProxy(ais)

    if isinstance(ai, str):
        ai = ut.u2b(ai)

    if isinstance(ai, bytes):
        ut.ep_assert(len(ai) >= 4, _("AIScript name too short"))

        if len(ai) > 4:
            if ai in DefAIScriptDict:
                return ut.b2i4(DefAIScriptDict[ai])
            sl = _("Cannot encode string {} as {}.").format(ai, "AIScript")
            for match in difflib.get_close_matches(ai, DefAIScriptDict.keys()):
                sl += "\n" + _(" - Suggestion: {}").format(match)

        elif len(ai) == 4:
            if ai in DefAIScriptDict.values():
                return ut.b2i4(ai)
            sl = _("Cannot encode string {} as {}.").format(ai, "AIScript")
            for match in difflib.get_close_matches(ai, DefAIScriptDict.values()):
                sl += "\n" + _(" - Suggestion: {}").format(match)
        raise ut.EPError(sl)

    if isinstance(ai, ConstType):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(ais, "AIScript"))
    assert not isinstance(ai, ExprProxy), "unreachable"
    return ai


@overload
def _EncodeAny(t: str, f: Callable, dl: Mapping[str, int], s: str | bytes) -> int:
    ...


@overload
def _EncodeAny(t: str, f: Callable, dl: Mapping[str, int], s: T) -> T:
    ...


@overload
def _EncodeAny(t: str, f: Callable, dl: Mapping[str, int], s: _ExprProxy) -> _Dword:
    ...


def _EncodeAny(t: str, f: Callable, dl: Mapping[str, int], s: _Arg) -> _Dword:  # noqa: N802
    if isinstance(s, int):
        return s

    u = ut.unProxy(s)

    if isinstance(u, (str, bytes)):  # noqa: UP038
        try:
            return f(u)
        except KeyError:
            if isinstance(u, str):
                if u in dl:
                    return dl[u]
                sl = _("Cannot encode string {} as {}.").format(u, t)
                for match in difflib.get_close_matches(u, dl.keys()):
                    sl += "\n" + _(" - Suggestion: {}").format(match)
                raise ut.EPError(sl)
            raise ut.EPError(_('[Warning] "{}" is not a {}').format(u, t))

    elif isinstance(u, ConstType):
        raise ut.EPError(_('[Warning] "{}" is not a {}').format(u, t))
    assert not isinstance(u, ExprProxy), "unreachable"
    return u


@overload
def EncodeLocation(loc: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeLocation(loc: T, issueError: bool = False) -> T:  # noqa: N803
    ...


@overload
def EncodeLocation(loc: _ExprProxy, issueError: bool = False) -> _Dword:  # noqa: N803
    ...


def EncodeLocation(loc: _Arg, issueError: bool = False) -> _Dword:  # noqa: N803, N802
    return _EncodeAny("location", GetLocationIndex, DefLocationDict, loc)


@overload
def EncodeString(s: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeString(s: T, issueError: bool = False) -> T:  # noqa: N803
    ...


@overload
def EncodeString(s: _ExprProxy, issueError: bool = False) -> _Dword:  # noqa: N803
    ...


def EncodeString(s: _Arg, issueError: bool = False) -> _Dword:  # noqa: N803, N802
    _def_string_dict: dict[str, int] = {}
    return _EncodeAny("MapString", GetStringIndex, _def_string_dict, s)


@overload
def EncodeSwitch(sw: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeSwitch(sw: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeSwitch(sw: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeSwitch(sw: __Arg, issueError: bool = False) -> _Byte:  # noqa: N803, N802
    return _EncodeAny("switch", GetSwitchIndex, DefSwitchDict, sw)  # type: ignore[return-value]


@overload
def EncodeUnit(u: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeUnit(u: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeUnit(u: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodeUnit(u: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("unit", GetUnitIndex, DefUnitDict, u)  # type: ignore[return-value]


@overload
def EncodeTBL(t: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeTBL(t: T, issueError: bool = False) -> T:  # noqa: N803
    ...


@overload
def EncodeTBL(t: _ExprProxy, issueError: bool = False) -> _Dword:  # noqa: N803
    ...


def EncodeTBL(t: _Arg, issueError: bool = False) -> _Dword:  # noqa: N803, N802
    # TODO: handle custom stat_txt.tbl
    return _EncodeAny("stat_txt.tbl", lambda s: {}[s], DefStatTextDict, t)


@overload
def EncodeFlingy(flingy: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeFlingy(flingy: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeFlingy(flingy: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodeFlingy(flingy: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("flingy", lambda s: {}[s], DefFlingyDict, flingy)  # type: ignore[return-value]


@overload
def EncodeIcon(icon: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeIcon(icon: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeIcon(icon: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodeIcon(icon: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("icon", lambda s: {}[s], DefIconDict, icon)  # type: ignore[return-value]


@overload
def EncodeSprite(sprite: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeSprite(sprite: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeSprite(sprite: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodeSprite(sprite: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("sprite", lambda s: {}[s], DefSpriteDict, sprite)  # type: ignore[return-value]


@overload
def EncodeImage(image: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeImage(image: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeImage(image: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodeImage(image: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("image", lambda s: {}[s], DefImageDict, image)  # type: ignore[return-value]


@overload
def EncodeIscript(iscript: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeIscript(iscript: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeIscript(iscript: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodeIscript(iscript: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("iscript", lambda s: {}[s], DefIscriptDict, iscript)  # type: ignore[return-value]


@overload
def EncodeUnitOrder(order: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeUnitOrder(order: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeUnitOrder(order: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeUnitOrder(order: __Arg, issueError: bool = False) -> _Byte:  # noqa: N803, N802
    return _EncodeAny("UnitOrder", lambda s: {}[s], DefUnitOrderDict, order)  # type: ignore[return-value]


@overload
def EncodeWeapon(weapon: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeWeapon(weapon: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeWeapon(weapon: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeWeapon(weapon: __Arg, issueError: bool = False) -> _Byte:  # noqa: N803, N802
    return _EncodeAny("weapon", lambda s: {}[s], DefWeaponDict, weapon)  # type: ignore[return-value]


@overload
def EncodeTech(tech: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeTech(tech: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeTech(tech: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeTech(tech: __Arg, issueError: bool = False) -> _Byte:  # noqa: N803, N802
    return _EncodeAny("tech", lambda s: {}[s], DefTechDict, tech)  # type: ignore[return-value]


@overload
def EncodeUpgrade(upgrade: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodeUpgrade(upgrade: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodeUpgrade(upgrade: __ExprProxy, issueError: bool = False) -> _Byte:  # noqa: N803
    ...


def EncodeUpgrade(upgrade: __Arg, issueError: bool = False) -> _Byte:  # noqa: N803, N802
    return _EncodeAny("upgrade", lambda s: {}[s], DefUpgradeDict, upgrade)  # type: ignore[return-value]


@overload
def EncodePortrait(portrait: str | bytes, issueError: bool = False) -> int:  # noqa: N803
    ...


@overload
def EncodePortrait(portrait: U, issueError: bool = False) -> U:  # noqa: N803
    ...


@overload
def EncodePortrait(portrait: __ExprProxy, issueError: bool = False) -> _Word:  # noqa: N803
    ...


def EncodePortrait(portrait: __Arg, issueError: bool = False) -> _Word:  # noqa: N803, N802
    return _EncodeAny("portrait", lambda s: {}[s], DefPortraitDict, portrait)  # type: ignore[return-value]
