#!/usr/bin/python
# Copyright 2024 by zzt (Defender).
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import enum
from typing import Final, Literal, Union

from .. import core as c
from .. import utils as ut
from ..localize import _
from . import unitdata
from .scdataobject import SCDataObject


class MemberKind(enum.Enum):
    # TODO: Combine with offsetmap's MemberKind
    # Get rid of boilerplate/duplicate codes later
    DWORD = enum.auto()
    WORD = enum.auto()
    BYTE = enum.auto()
    BOOL = enum.auto()
    TRG_UNIT = enum.auto()
    TRG_PLAYER = enum.auto()
    UNIT_ORDER = enum.auto()
    POSITION = enum.auto()
    POSITION_X = enum.auto()
    POSITION_Y = enum.auto()
    FLINGY = enum.auto()
    SPRITE = enum.auto()
    UPGRADE = enum.auto()
    TECH = enum.auto()
    # More to be added!

    def cast(self, other):
        match self:
            case MemberKind.TRG_UNIT:
                return c.EncodeUnit(other)
            case MemberKind.TRG_PLAYER:
                return c.EncodePlayer(other)
            case MemberKind.UNIT_ORDER:
                return c.EncodeUnitOrder(other)
            case MemberKind.FLINGY:
                return c.EncodeFlingy(other)
            case MemberKind.SPRITE:
                return c.EncodeSprite(other)
            case MemberKind.UPGRADE:
                return c.EncodeUpgrade(other)
            case MemberKind.TECH:
                return c.EncodeTech(other)
            case _:
                return other

    @property
    def size(self) -> Literal[1, 2, 4]:
        match self:
            case MemberKind.DWORD | MemberKind.POSITION:
                return 4
            case (
                MemberKind.WORD
                | MemberKind.TRG_UNIT
                | MemberKind.POSITION_X
                | MemberKind.POSITION_Y
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

class SCDataObjectMember:
    base_address: Final[int]
    base_address_epd: Final[int]
    kind: Final[MemberKind]

    def __init__(self, base_address, kind: MemberKind) -> None:
        ut.ep_assert(base_address % 4 == 0, _("Malaligned member"))
        # ut.ep_assert(base_address % 4 + kind.size <= 4, _("Malaligned member"))
        self.base_address = base_address
        self.base_address_epd = ut.EPD(base_address)
        self.kind = kind

    def __get__(self, obj, objtype=None) -> Union[ut.ExprProxy, "SCDataObject"]:
        from .scdataobject import SCDataObject

        if obj is None:
            return self
        # TODO improve performance for the cases not divisible by 4
        # Probably epdoffsetmap code can be referenced

        if isinstance(obj, SCDataObject):
            if self.kind.size == 4:
                q, r = obj, 0
            else:
                q, r = divmod(obj * self.kind.size, 4)
            return self.kind.read_epd(self.base_address_epd + q, r)
        raise AttributeError("SCDataObjectMember owner not of type SCDataObject!")


    def __set__(self, obj, value) -> None:
        from .scdataobject import SCDataObject

        if isinstance(obj, SCDataObject):
            if self.kind.size == 4:
                q, r = obj, 0
            else:
                q, r = divmod(obj * self.kind.size, 4)
            value = self.kind.cast(value)
            self.kind.write_epd(self.base_address_epd + q, r, value)
            return
        raise AttributeError
