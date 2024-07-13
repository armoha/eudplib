#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from typing import TypeAlias, TypeVar, cast

from .. import core as c
from .. import utils as ut
from ..localize import _
from .epdoffsetmap import EPDOffsetMap, _epd_cache, _ptr_cache
from .member import (
    Flag,
    StructEnumMember,
    StructMember,
)
from .member import MemberKind as Mk


class CSpriteFlags(StructEnumMember):
    __slots__ = ()
    DrawSelCircle = Flag(0x01)  # Draw selection circle
    AllySel1 = Flag(0x02)
    AllySel2 = Flag(0x04)
    Selected = Flag(0x08)  # Draw HP bar, Selected
    Flag4 = Flag(0x10)
    Hidden = Flag(0x20)  # Hidden
    Burrowed = Flag(0x40)  # Burrowed
    IscriptCode = Flag(0x80)  # Iscript unbreakable code section


T = TypeVar("T", bound="CSprite")
int_or_var: TypeAlias = int | c.EUDVariable | ut.ExprProxy


# ruff: noqa: N815
class CSprite(EPDOffsetMap):
    __slots__ = ("_ptr",)
    prev = StructMember(0x00, Mk.C_SPRITE)
    next = StructMember(0x04, Mk.C_SPRITE)
    sprite = StructMember(0x08, Mk.SPRITE)
    playerID = StructMember(0x0A, Mk.PLAYER)  # officially "creator"
    # 0 <= selectionIndex <= 11.
    # Index in the selection area at bottom of screen.
    selectionIndex = StructMember(0x0B, Mk.BYTE)
    # Player bits indicating the visibility for a player
    # (not hidden by the fog-of-war)
    visibilityFlags = StructMember(0x0C, Mk.BYTE)
    elevationLevel = StructMember(0x0D, Mk.BYTE)
    flags = CSpriteFlags(0x0E, Mk.BYTE)
    selectionTimer = StructMember(0x0F, Mk.BYTE)
    index = StructMember(0x10, Mk.WORD)
    unknown0x12 = StructMember(0x12, Mk.BYTE)
    unknown0x13 = StructMember(0x13, Mk.BYTE)
    pos = StructMember(0x14, Mk.POSITION)
    posX = StructMember(0x14, Mk.POSITION_X)
    posY = StructMember(0x16, Mk.POSITION_Y)
    mainGraphic = StructMember(0x18, Mk.DWORD)  # officially "pImagePrimary"
    imageHead = StructMember(0x1C, Mk.DWORD)
    imageTail = StructMember(0x20, Mk.DWORD)

    def __init__(self, epd: int_or_var, *, ptr: int_or_var | None = None) -> None:
        """
        EPD Constructor of CSprite.

        Use CSprite.from_ptr(ptr) for ptr value
        """
        _epd: int | c.EUDVariable
        self._ptr: int | c.EUDVariable | None

        if not isinstance(epd, CSprite):
            u, p = ut.unProxy(epd), ut.unProxy(ptr)
        else:
            u, p = epd._epd, epd._ptr
        if isinstance(u, int):
            if p is not None and not isinstance(p, int):
                raise ut.EPError(
                    _("Invalid input for CSprite: {}").format((epd, ptr))
                )
            q, r = divmod(u - ut.EPD(0x629D98), 9)  # check epd
            if r == 0 and 0 <= q < 2500:
                _epd, self._ptr = u, 0x629D98 + 36 * q
            else:
                raise ut.EPError(
                    _("Invalid input for CSprite: {}").format((epd, ptr))
                )
        elif isinstance(u, c.EUDVariable):
            if p is not None:
                if not isinstance(p, c.EUDVariable):
                    raise ut.EPError(
                        _("Invalid input for CSprite: {}").format((epd, ptr))
                    )
                _epd, self._ptr = c.EUDCreateVariables(2)
                c.SetVariables((_epd, self._ptr), (u, p))
            else:
                self._ptr = None
                _epd = c.EUDVariable()
                _epd << u
        else:
            raise ut.EPError(_("Invalid input for CSprite: {}").format((epd, ptr)))

        super().__init__(_epd)

    @classmethod
    def cast(cls: type[T], _from: int_or_var) -> T:
        return cls(_from)

    @classmethod
    def from_ptr(cls: type[T], ptr: int_or_var) -> T:
        epd: int | c.EUDVariable
        u = ut.unProxy(ptr)
        # check ptr
        if isinstance(u, int):
            q, r = divmod(u - 0x59CCA8, 336)
            if r == 0 and 0 <= q < 1700:
                epd = ut.EPD(u)
            else:
                raise ut.EPError(_("Invalid input for CSprite: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            epd = _epd_cache(u)
        else:
            raise ut.EPError(_("Invalid input for CSprite: {}").format(epd))

        return cls(epd, ptr=u)

    @classmethod
    def from_read(cls: type[T], epd) -> T:
        from ..memio import f_spriteepdread_epd

        _ptr, _epd = f_spriteepdread_epd(epd)
        return cls(_epd, ptr=_ptr)

    @property
    def ptr(self) -> int | c.EUDVariable:
        if self._ptr is not None:
            return self._ptr
        return _ptr_cache(cast(c.EUDVariable, self._epd))
