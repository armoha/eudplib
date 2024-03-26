#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import enum
from abc import ABCMeta
from types import NoneType
from typing import (
    TYPE_CHECKING,
    Final,
    Generic,
    Literal,
    Self,
    TypeVar,
    overload,
)

from .. import core as c
from .. import utils as ut
from ..localize import _
from .scdataobject import SCDataObject

if TYPE_CHECKING:
    # F401 refers to "unused import"
    # Ruff is currently not correctly detecting in-quote references in Generic
    # which is why those imports are marked as unused by default
    # Therefore, these F401 warnings are suppressed now
    from .flingydata import FlingyData  # noqa: F401
    from .imagedata import ImageData  # noqa: F401
    from .playerdata import PlayerData  # noqa: F401
    from .spritedata import SpriteData  # noqa: F401
    from .unitdata import UnitData  # noqa: F401
    from .unitorderdata import UnitOrderData  # noqa: F401
    from .weapondata import WeaponData  # noqa: F401

class MemberKind(enum.Enum):
    # TODO: Combine with offsetmap's MemberKind
    # Get rid of boilerplate/duplicate codes later
    DWORD = enum.auto()
    WORD = enum.auto()
    BYTE = enum.auto()
    BOOL = enum.auto()
    UNIT = enum.auto()
    PLAYER = enum.auto()
    UNIT_ORDER = enum.auto()
    POSITION = enum.auto()
    POSITION_X = enum.auto()
    POSITION_Y = enum.auto()
    DIMENSIONS = enum.auto()
    DIMENSIONS_X = enum.auto()
    DIMENSIONS_Y = enum.auto()
    FLINGY = enum.auto()
    SPRITE = enum.auto()
    UPGRADE = enum.auto()
    TECH = enum.auto()
    WEAPON = enum.auto()
    IMAGE = enum.auto()
    # More to be added!

    def cast(self, other):
        match self:
            case MemberKind.UNIT:
                from . import unitdata
                return unitdata.UnitData(other)
            case MemberKind.PLAYER:
                return c.EncodePlayer(other)
            case MemberKind.UNIT_ORDER:
                from . import unitorderdata
                return unitorderdata.UnitOrderData(other)
            case MemberKind.FLINGY:
                from . import flingydata
                return flingydata.FlingyData(other)
            case MemberKind.SPRITE:
                return c.EncodeSprite(other)
            case MemberKind.UPGRADE:
                return c.EncodeUpgrade(other)
            case MemberKind.TECH:
                return c.EncodeTech(other)
            case MemberKind.WEAPON:
                from . import weapondata
                return weapondata.WeaponData(other)
            case MemberKind.SPRITE:
                from . import spritedata
                return spritedata.SpriteData(other)
            case _:
                return other

    @property
    def size(self) -> Literal[1, 2, 4]:
        match self:
            case MemberKind.DWORD | MemberKind.POSITION | MemberKind.DIMENSIONS:
                return 4
            case (
                MemberKind.WORD
                | MemberKind.UNIT
                | MemberKind.POSITION_X
                | MemberKind.POSITION_Y
                | MemberKind.DIMENSIONS_X
                | MemberKind.DIMENSIONS_Y
                | MemberKind.FLINGY
                | MemberKind.SPRITE
            ):
                return 2
            case _:
                return 1

    def read_epd(self, epd, subp) -> ut.ExprProxy | SCDataObject:
        from ..eudlib import memiof
        match self.size:
            case 4:
                value = memiof.f_dwread_epd(epd)
            case 2:
                value = memiof.f_wread_epd(epd, subp)
            case 1:
                value = memiof.f_bread_epd(epd, subp)
            case _:
                raise ValueError("size of MemberKind not in 1, 2, 4")

        return self.cast(value)

    def write_epd(self, epd, subp, value) -> None:
        from ..eudlib import memiof
        match self.size:
            case 4:
                memiof.f_dwwrite_epd(epd, value)
            case 2:
                memiof.f_wwrite_epd(epd, subp, value)
            case 1:
                memiof.f_bwrite_epd(epd, subp, value)
            case _:
                raise ValueError("size of MemberKind not in 1, 2, 4")

class Member:
    base_address: Final[int]
    base_address_epd: Final[int]
    kind: Final[MemberKind]

    def __init__(self, base_address: int, kind: MemberKind) -> None:
        ut.ep_assert(base_address % 4 == 0, _("Malaligned member"))
        # ut.ep_assert(base_address % 4 + kind.size <= 4, _("Malaligned member"))
        self.base_address = base_address
        self.base_address_epd = ut.EPD(base_address)
        self.kind = kind

    @overload
    def __get__(self, instance: NoneType, objtype=None) -> Self:
        ...

    @overload
    def __get__(
            self, instance: SCDataObject, objtype=None
        ) -> ut.ExprProxy | SCDataObject:
        ...

    def __get__(
            self, instance, objtype=None
        ):
        from .scdataobject import SCDataObject

        if instance is None:
            return self
        # TODO improve performance for the cases not divisible by 4 by caching
        # Probably epdoffsetmap code can be referenced

        if isinstance(instance, SCDataObject):
            if self.kind.size == 4:
                q, r = instance, 0
            else:
                q, r = c.f_div(instance * self.kind.size, 4)
            return self.kind.read_epd(self.base_address_epd + q, r)
        raise AttributeError("SCDataObjectMember owner not of type SCDataObject!")


    def __set__(self, instance, value) -> None:
        from .scdataobject import SCDataObject

        if isinstance(instance, SCDataObject):
            if self.kind.size == 4:
                q, r = instance, 0
            else:
                q, r = c.f_div(instance * self.kind.size, 4)
            value = self.kind.cast(value)
            self.kind.write_epd(self.base_address_epd + q, r, value)
            return
        raise AttributeError

class EnumMember(Member):
    # TODO: Implement this later
    def __init__(self, base_address: int, kind: MemberKind) -> NoneType:
        raise NotImplementedError("EnumMember is not implemented yet")

M = TypeVar("M", bound=SCDataObject)

class SCDataObjectTypeMember(Member, Generic[M], metaclass=ABCMeta):
    # TODO Think of a better name?
    _data_object_type: type[M]
    _default_kind: MemberKind

    def __init__(self, base_address: int) -> NoneType:
        super().__init__(base_address, self._default_kind)

    @overload
    def __get__(self, instance: NoneType, objtype=None) -> Self:
        ...

    @overload
    def __get__(self, instance: SCDataObject, objtype=None) -> M:
        ...

    def __get__(self, instance, objtype=None):
        if instance is None:
            return self
        return self._data_object_type(super().__get__(instance))

class FlingyDataMember(SCDataObjectTypeMember["FlingyData"]):
    _default_kind = MemberKind.FLINGY

class ImageDataMember(SCDataObjectTypeMember["ImageData"]):
    _default_kind = MemberKind.IMAGE

class PlayerDataMember(SCDataObjectTypeMember["PlayerData"]):
    _default_kind = MemberKind.PLAYER

class SpriteDataMember(SCDataObjectTypeMember["SpriteData"]):
    _default_kind = MemberKind.SPRITE

class UnitDataMember(SCDataObjectTypeMember["UnitData"]):
    _default_kind = MemberKind.UNIT

class UnitOrderDataMember(SCDataObjectTypeMember["UnitOrderData"]):
    _default_kind = MemberKind.UNIT_ORDER

class WeaponDataMember(SCDataObjectTypeMember["WeaponData"]):
    _default_kind = MemberKind.WEAPON

