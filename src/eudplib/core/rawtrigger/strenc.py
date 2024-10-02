# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import difflib
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, TypeAlias, overload

from ... import utils as ut
from ...localize import _
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
def EncodeAIScript(ais: str | bytes) -> int:
    ...


@overload
def EncodeAIScript(ais: T) -> T:
    ...


@overload
def EncodeAIScript(ais: _ExprProxy) -> _Dword:
    ...


def EncodeAIScript(ais: _Arg) -> _Dword:  # noqa: N802
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
        raise ut.EPError(_('"{}" is not a {}').format(ais, "AIScript"))
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
            raise ut.EPError(_('"{}" is not a {}').format(u, t))

    elif isinstance(u, ConstType):
        raise ut.EPError(_('"{}" is not a {}').format(u, t))
    assert not isinstance(u, ExprProxy), "unreachable"
    return u


@overload
def EncodeLocation(loc: str | bytes) -> int:
    ...


@overload
def EncodeLocation(loc: T) -> T:
    ...


@overload
def EncodeLocation(loc: _ExprProxy) -> _Dword:
    ...


def EncodeLocation(loc: _Arg) -> _Dword:  # noqa: N802
    return _EncodeAny("location", GetLocationIndex, DefLocationDict, loc)


@overload
def EncodeString(s: str | bytes) -> int:
    ...


@overload
def EncodeString(s: T) -> T:
    ...


@overload
def EncodeString(s: _ExprProxy) -> _Dword:
    ...


def EncodeString(s: _Arg) -> _Dword:  # noqa: N802
    _def_string_dict: dict[str, int] = {}
    return _EncodeAny("MapString", GetStringIndex, _def_string_dict, s)


@overload
def EncodeSwitch(sw: str | bytes) -> int:
    ...


@overload
def EncodeSwitch(sw: U) -> U:
    ...


@overload
def EncodeSwitch(sw: __ExprProxy) -> _Byte:
    ...


def EncodeSwitch(sw: __Arg) -> _Byte:  # noqa: N802
    return _EncodeAny("switch", GetSwitchIndex, DefSwitchDict, sw)  # type: ignore[return-value]


@overload
def EncodeUnit(u: str | bytes) -> int:
    ...


@overload
def EncodeUnit(u: U) -> U:
    ...


@overload
def EncodeUnit(u: __ExprProxy) -> _Word:
    ...


def EncodeUnit(u: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("unit", GetUnitIndex, DefUnitDict, u)  # type: ignore[return-value]


@overload
def EncodeTBL(t: str | bytes) -> int:
    ...


@overload
def EncodeTBL(t: T) -> T:
    ...


@overload
def EncodeTBL(t: _ExprProxy) -> _Dword:
    ...


def EncodeTBL(t: _Arg) -> _Dword:  # noqa: N802
    # TODO: handle custom stat_txt.tbl
    return _EncodeAny("stat_txt.tbl", lambda s: {}[s], DefStatTextDict, t)


@overload
def EncodeFlingy(flingy: str | bytes) -> int:
    ...


@overload
def EncodeFlingy(flingy: U) -> U:
    ...


@overload
def EncodeFlingy(flingy: __ExprProxy) -> _Word:
    ...


def EncodeFlingy(flingy: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("flingy", lambda s: {}[s], DefFlingyDict, flingy)  # type: ignore[return-value]


@overload
def EncodeIcon(icon: str | bytes) -> int:
    ...


@overload
def EncodeIcon(icon: U) -> U:
    ...


@overload
def EncodeIcon(icon: __ExprProxy) -> _Word:
    ...


def EncodeIcon(icon: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("icon", lambda s: {}[s], DefIconDict, icon)  # type: ignore[return-value]


@overload
def EncodeSprite(sprite: str | bytes) -> int:
    ...


@overload
def EncodeSprite(sprite: U) -> U:
    ...


@overload
def EncodeSprite(sprite: __ExprProxy) -> _Word:
    ...


def EncodeSprite(sprite: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("sprite", lambda s: {}[s], DefSpriteDict, sprite)  # type: ignore[return-value]


@overload
def EncodeImage(image: str | bytes) -> int:
    ...


@overload
def EncodeImage(image: U) -> U:
    ...


@overload
def EncodeImage(image: __ExprProxy) -> _Word:
    ...


def EncodeImage(image: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("image", lambda s: {}[s], DefImageDict, image)  # type: ignore[return-value]


@overload
def EncodeIscript(iscript: str | bytes) -> int:
    ...


@overload
def EncodeIscript(iscript: U) -> U:
    ...


@overload
def EncodeIscript(iscript: __ExprProxy) -> _Word:
    ...


def EncodeIscript(iscript: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("iscript", lambda s: {}[s], DefIscriptDict, iscript)  # type: ignore[return-value]


@overload
def EncodeUnitOrder(order: str | bytes) -> int:
    ...


@overload
def EncodeUnitOrder(order: U) -> U:
    ...


@overload
def EncodeUnitOrder(order: __ExprProxy) -> _Byte:
    ...


def EncodeUnitOrder(order: __Arg) -> _Byte:  # noqa: N802
    return _EncodeAny("UnitOrder", lambda s: {}[s], DefUnitOrderDict, order)  # type: ignore[return-value]


@overload
def EncodeWeapon(weapon: str | bytes) -> int:
    ...


@overload
def EncodeWeapon(weapon: U) -> U:
    ...


@overload
def EncodeWeapon(weapon: __ExprProxy) -> _Byte:
    ...


def EncodeWeapon(weapon: __Arg) -> _Byte:  # noqa: N802
    return _EncodeAny("weapon", lambda s: {}[s], DefWeaponDict, weapon)  # type: ignore[return-value]


@overload
def EncodeTech(tech: str | bytes) -> int:
    ...


@overload
def EncodeTech(tech: U) -> U:
    ...


@overload
def EncodeTech(tech: __ExprProxy) -> _Byte:
    ...


def EncodeTech(tech: __Arg) -> _Byte:  # noqa: N802
    return _EncodeAny("tech", lambda s: {}[s], DefTechDict, tech)  # type: ignore[return-value]


@overload
def EncodeUpgrade(upgrade: str | bytes) -> int:
    ...


@overload
def EncodeUpgrade(upgrade: U) -> U:
    ...


@overload
def EncodeUpgrade(upgrade: __ExprProxy) -> _Byte:
    ...


def EncodeUpgrade(upgrade: __Arg) -> _Byte:  # noqa: N802
    return _EncodeAny("upgrade", lambda s: {}[s], DefUpgradeDict, upgrade)  # type: ignore[return-value]


@overload
def EncodePortrait(portrait: str | bytes) -> int:
    ...


@overload
def EncodePortrait(portrait: U) -> U:
    ...


@overload
def EncodePortrait(portrait: __ExprProxy) -> _Word:
    ...


def EncodePortrait(portrait: __Arg) -> _Word:  # noqa: N802
    return _EncodeAny("portrait", lambda s: {}[s], DefPortraitDict, portrait)  # type: ignore[return-value]
