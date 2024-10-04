# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

# ruff: noqa: N815
from typing import ClassVar, TypeAlias, TypeVar, cast

from .. import core as c
from ..localize import _
from ..utils import EPD, EPError, ExprProxy, classproperty, unProxy
from .offsetmap import (
    ByteEnumMember,
    ByteMember,
    CSpriteMember,
    DwordMember,
    EPDOffsetMap,
    Flag,
    PlayerMember,
    PositionMember,
    PositionXMember,
    PositionYMember,
    SpriteMember,
    WordMember,
)
from .offsetmap.epdoffsetmap import _epd_cache, _ptr_cache


class CSpriteFlags(ByteEnumMember):
    __slots__ = ()
    DrawSelCircle = Flag(0x01)
    "Draw selection circle"
    AllySel1 = Flag(0x02)
    AllySel2 = Flag(0x04)
    Selected = Flag(0x08)
    "Draw HP bar, Selected"
    IsSubunit = Flag(0x10)
    "sorts sprite elevation higher, so that subunits always appear above base unit"
    Hidden = Flag(0x20)
    Burrowed = Flag(0x40)
    IscriptCode = Flag(0x80)
    "Iscript unbreakable code section"


T = TypeVar("T", bound="CSprite")
int_or_var: TypeAlias = int | c.EUDVariable | ExprProxy


class CSprite(EPDOffsetMap):
    __slots__ = ("_ptr",)
    prev: ClassVar = CSpriteMember("struct", 0x00)
    next: ClassVar = CSpriteMember("struct", 0x04)
    sprite: ClassVar = SpriteMember("struct", 0x08)
    player: ClassVar = PlayerMember("struct", 0x0A)
    "officially 'creator'"
    selectionIndex: ClassVar = ByteMember("struct", 0x0B)
    "0 <= selectionIndex <= 11. Index in the selection area at bottom of screen."
    visibilityFlags: ClassVar = ByteMember("struct", 0x0C)
    "Player bits indicating visibility for a player (not hidden by the fog-of-war)"
    elevationLevel: ClassVar = ByteMember("struct", 0x0D)
    flags = CSpriteFlags("struct", 0x0E)
    selectionTimer: ClassVar = ByteMember("struct", 0x0F)
    index: ClassVar = WordMember("struct", 0x10)
    grpWidth: ClassVar = ByteMember("struct", 0x12)
    grpHeight: ClassVar = ByteMember("struct", 0x13)
    pos: ClassVar = PositionMember("struct", 0x14)
    posX: ClassVar = PositionXMember("struct", 0x14)
    posY: ClassVar = PositionYMember("struct", 0x16)
    mainGraphic: ClassVar = DwordMember("struct", 0x18)
    "officially 'pImagePrimary', CImage"
    imageHead: ClassVar = DwordMember("struct", 0x1C)
    imageTail: ClassVar = DwordMember("struct", 0x20)

    @classproperty
    def range(self):
        return (EPD(0x629D98), EPD(0x629D98) + 9 * 2499, 9)

    def __init__(self, epd: int_or_var, *, ptr: int_or_var | None = None) -> None:
        """EPD Constructor of CSprite. Use CSprite.from_ptr(ptr) for ptr value"""
        _epd: int | c.EUDVariable
        self._ptr: int | c.EUDVariable | None

        if not isinstance(epd, CSprite):
            u, p = unProxy(epd), unProxy(ptr)
        else:
            u, p = epd._value, epd._ptr

        if isinstance(u, int):
            q, r = divmod(u - EPD(0x629D98), 9)  # check epd
            if r == 0 and 0 <= q < 2500:
                _epd, self._ptr = u, 0x629D98 + 36 * q
            else:
                raise EPError(_("Invalid input for CSprite: {}").format(epd))

            if p is not None and not isinstance(p, int) or p != self._ptr:
                raise EPError(_("Invalid input for CSprite.ptr: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            if p is None:
                self._ptr = None
                if EPDOffsetMap._cast:
                    _epd = u
                else:
                    _epd = c.EUDVariable()
                    _epd << u

            else:
                if not isinstance(p, c.EUDVariable):
                    raise EPError(_("Invalid input for CSprite.ptr: {}").format(ptr))
                if EPDOffsetMap._cast:
                    _epd, self._ptr = u, p
                else:
                    _epd, self._ptr = c.EUDCreateVariables(2)
                    c.SetVariables((_epd, self._ptr), (u, p))
        else:
            raise EPError(_("Invalid input for CSprite: {}").format(epd))

        EPDOffsetMap._cast = False
        super().__init__(_epd)

    @classmethod
    def from_ptr(cls: type[T], ptr: int_or_var) -> T:
        epd: int | c.EUDVariable
        u = unProxy(ptr)
        # check ptr
        if isinstance(u, int):
            q, r = divmod(u - 0x629D98, 36)
            if r == 0 and 0 <= q < 2500:
                epd = EPD(u)
            else:
                raise EPError(_("Invalid input for CSprite: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            epd = _epd_cache(u)
        else:
            raise EPError(_("Invalid input for CSprite: {}").format(epd))

        return cls(epd, ptr=u)

    @classmethod
    def from_read(cls: type[T], epd) -> T:
        from ..memio import f_spriteepdread_epd

        _ptr, _epd = f_spriteepdread_epd(epd)
        return cls(_epd, ptr=_ptr)

    @property
    def ptr(self) -> int | c.EUDVariable:
        if isinstance(self._value, int):
            return cast(int, self._ptr)  # FIXME
        if self._ptr is None:
            self._ptr = c.EUDVariable()
        return _ptr_cache(self._value, self._ptr)
