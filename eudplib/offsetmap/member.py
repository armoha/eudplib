#!/usr/bin/python
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import enum
from abc import ABCMeta, abstractmethod
from typing import (
    TYPE_CHECKING,
    Final,
    Generic,
    Literal,
    NoReturn,
    TypeVar,
    overload,
)

from typing_extensions import Self

from .. import core as c
from .. import ctrlstru as cs
from .. import scdata
from .. import utils as ut
from ..localize import _
from ..trigger import Trigger

if TYPE_CHECKING:
    from .csprite import CSprite
    from .cunit import CUnit
    from .epdoffsetmap import EPDOffsetMap


class MemberKind(enum.Enum):
    __slots__ = ()
    DWORD = enum.auto()
    WORD = enum.auto()
    BYTE = enum.auto()
    BOOL = enum.auto()
    C_UNIT = enum.auto()
    C_SPRITE = enum.auto()
    UNIT = enum.auto()
    PLAYER = enum.auto()
    UNIT_ORDER = enum.auto()
    POSITION = enum.auto()
    POSITION_X = enum.auto()
    POSITION_Y = enum.auto()
    FLINGY = enum.auto()
    SPRITE = enum.auto()
    UPGRADE = enum.auto()
    TECH = enum.auto()

    def cast(self, other):
        match self:
            case MemberKind.UNIT:
                return c.EncodeUnit(other)
            case MemberKind.PLAYER:
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
            case (
                MemberKind.DWORD
                | MemberKind.C_UNIT
                | MemberKind.C_SPRITE
                | MemberKind.POSITION
            ):
                return 4
            case (
                MemberKind.WORD
                | MemberKind.UNIT
                | MemberKind.POSITION_X
                | MemberKind.POSITION_Y
                | MemberKind.FLINGY
                | MemberKind.SPRITE
            ):
                return 2
            case _:
                return 1

    def read_epd(self, epd, subp) -> c.EUDVariable:
        from ..eudlib.memiof import (
            f_bread_epd,
            f_cunitepdread_epd,
            f_dwread_epd,
            f_epdspriteread_epd,
            f_maskread_epd,
            f_readgen_epd,
            f_wread_epd,
        )
        from ..eudlib.memiof.memifgen import _map_xy_mask

        match self:
            case MemberKind.BOOL:
                shift = 8 * subp
                f_boolread_epd = f_readgen_epd(1 << shift, (0, lambda x: 1))
                return f_boolread_epd(epd)
            case MemberKind.C_UNIT:
                return f_cunitepdread_epd(epd)
            case MemberKind.C_SPRITE:
                return f_epdspriteread_epd(epd)
            case MemberKind.UNIT | MemberKind.FLINGY:
                return f_bread_epd(epd, subp)
            case MemberKind.POSITION:
                return f_maskread_epd(
                    epd, (lambda x, y: x + 65536 * y)(*_map_xy_mask())
                )
            case MemberKind.POSITION_X:
                shift = 8 * subp
                f_xread_epd = f_readgen_epd(
                    _map_xy_mask()[0] << shift, (0, lambda x: x >> shift)
                )
                return f_xread_epd(epd)
            case MemberKind.POSITION_Y:
                shift = 8 * subp
                f_yread_epd = f_readgen_epd(
                    _map_xy_mask()[1] << shift, (0, lambda x: x >> shift)
                )
                return f_yread_epd(epd)
            case _:
                match self.size:
                    case 4:
                        return f_dwread_epd(epd)
                    case 2:
                        return f_wread_epd(epd, subp)
                    case 1:
                        return f_bread_epd(epd, subp)
                raise AttributeError

    def write_epd(self, epd, subp, value) -> None:
        from ..eudlib.memiof import f_bwrite_epd, f_dwwrite_epd, f_wwrite_epd

        match self.size:
            case 4:
                f_dwwrite_epd(epd, value)
            case 2:
                f_wwrite_epd(epd, subp, value)
            case 1:
                f_bwrite_epd(epd, subp, value)

    def add_epd(self, epd, subp, value) -> None:
        from ..eudlib.memiof import f_badd_epd, f_dwadd_epd, f_wadd_epd

        match self.size:
            case 4:
                f_dwadd_epd(epd, value)
            case 2:
                f_wadd_epd(epd, subp, value)
            case 1:
                f_badd_epd(epd, subp, value)

    def subtract_epd(self, epd, subp, value) -> None:
        from ..eudlib.memiof import (
            f_bsubtract_epd,
            f_dwsubtract_epd,
            f_wsubtract_epd,
        )

        match self.size:
            case 4:
                f_dwsubtract_epd(epd, value)
            case 2:
                f_wsubtract_epd(epd, subp, value)
            case 1:
                f_bsubtract_epd(epd, subp, value)


class BaseMember(metaclass=ABCMeta):
    """Base descriptor class for EPDOffsetMap"""

    __slots__ = ()

    offset: Final[int]
    kind: Final[MemberKind]

    def __init__(self, offset: int, kind: MemberKind) -> None:
        ut.ep_assert(offset % 4 + kind.size <= 4, _("Malaligned member"))
        self.offset = offset  # type: ignore[misc]
        self.kind = kind  # type: ignore[misc]

    @abstractmethod
    def __get__(self, instance, owner=None):
        ...

    @abstractmethod
    def __set__(self, instance, value) -> None:
        ...


class UnsupportedMember(BaseMember):
    """Not supported EUD"""

    __slots__ = ("offset", "kind", "name")

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None) -> "UnsupportedMember":
        if instance is None:
            return self
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))

    def __set__(self, instance, value) -> NoReturn:
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))


class Member(BaseMember):
    """Descriptor for EPDOffsetMap"""

    __slots__ = ("offset", "kind")

    def __get__(self, instance, owner=None) -> "c.EUDVariable | Member":
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            return self.kind.read_epd(instance._epd + q, r)
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            value = self.kind.cast(value)
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


class EnumMember(BaseMember, ut.ExprProxy):
    __slots__ = ("offset", "kind", "_epd")

    def __init__(self, offset: int, kind: MemberKind) -> None:
        self._epd: int | c.EUDVariable = 0  # FIXME
        super().__init__(offset, kind)
        super(BaseMember, self).__init__(None)

    # FIXME: Overwriting ExprProxy.getValue is kinda hacky...
    def getValue(self):  # noqa: N802
        from ..eudlib.memiof import f_maskread_epd

        q, r = divmod(self.offset, 4)
        mask = ((1 << (8 * self.kind.size)) - 1) << (8 * r)
        return f_maskread_epd(self._epd + q, mask)

    def __get__(self, instance, owner=None) -> "EnumMember":
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            self._epd = instance._epd
            return self
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            value = self.kind.cast(value)
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


class Flag:
    __slots__ = ("mask",)

    mask: Final[int]

    def __init__(self, mask: int) -> None:
        self.mask = mask

    def __get__(self, instance, owner=None) -> c.EUDVariable:
        if isinstance(instance, EnumMember):
            q, r = divmod(instance.offset, 4)
            epd = instance._epd + q
            mask = self.mask << (8 * r)
            ret = c.EUDVariable()
            ret << True
            Trigger(
                c.MemoryXEPD(epd, c.AtMost, mask - 1, mask), ret.SetNumber(False)
            )
            return ret
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from ..eudlib.memiof import f_maskwrite_epd

        if isinstance(instance, EnumMember):
            q, r = divmod(instance.offset, 4)
            epd = instance._epd + q
            mask = self.mask << (8 * r)
            f_maskwrite_epd(epd, ~0, mask)
            if cs.EUDIfNot()(value):
                f_maskwrite_epd(epd, 0, mask)
            cs.EUDEndIf()
            return
        raise AttributeError


class CUnitMember(BaseMember):
    """Descriptor for EPDOffsetMap"""

    __slots__ = ("offset", "kind")

    def __init__(self, offset: int) -> None:
        ut.ep_assert(offset % 4 == 0)
        super().__init__(offset, MemberKind.C_UNIT)

    def __get__(self, instance, owner=None) -> "CUnit | CUnitMember":
        from .cunit import CUnit
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            return CUnit.from_read(instance._epd + self.offset // 4)
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .cunit import CUnit
        from .epdoffsetmap import EPDOffsetMap

        q, r = divmod(self.offset, 4)
        if isinstance(value, CUnit):
            value = value.ptr
        if isinstance(instance, EPDOffsetMap):
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


class CSpriteMember(BaseMember):
    """Descriptor for EPDOffsetMap"""

    __slots__ = ("offset", "kind")

    def __init__(self, offset: int) -> None:
        super().__init__(offset, MemberKind.C_SPRITE)

    def __get__(self, instance, owner=None) -> "CSprite | CSpriteMember":
        from .csprite import CSprite
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        if isinstance(instance, EPDOffsetMap):
            return CSprite.from_read(instance._epd + self.offset // 4)
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .csprite import CSprite
        from .epdoffsetmap import EPDOffsetMap

        q, r = divmod(self.offset, 4)
        if isinstance(value, CSprite):
            value = value.ptr
        if isinstance(instance, EPDOffsetMap):
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


S = TypeVar("S", bound=scdata.SCDataObject)


class SCDataObjectMember(BaseMember, Generic[S], metaclass=ABCMeta):
    """Descriptor for EPDOffsetMap"""

    bound_data_type: type[S]
    bound_kind: MemberKind

    def __init_subclass__(cls, data_type: type[S], kind: MemberKind) -> None:
        cls.bound_data_type = data_type
        cls.bound_kind = kind

    def __init__(self, offset: int) -> None:
        super().__init__(offset, self.bound_kind)

    @overload
    def __get__(self, instance: None, owner=None) -> Self:
        ...

    @overload
    def __get__(self, instance: "EPDOffsetMap", owner=None) -> S:
        ...

    def __get__(self, instance, owner=None):
        from .epdoffsetmap import EPDOffsetMap

        if instance is None:
            return self
        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            return self.bound_data_type(self.kind.read_epd(instance._epd + q, r))
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .epdoffsetmap import EPDOffsetMap

        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            value = self.kind.cast(value)
            self.kind.write_epd(instance._epd + q, r, value)
        else:
            raise AttributeError


class UnitDataMember(
    SCDataObjectMember[scdata.UnitData],
    data_type=scdata.UnitData,
    kind=MemberKind.UNIT,
):
    pass


class UnitOrderDataMember(
    SCDataObjectMember[scdata.UnitOrderData],
    data_type=scdata.UnitOrderData,
    kind=MemberKind.UNIT_ORDER,
):
    pass


class FlingyDataMember(
    SCDataObjectMember[scdata.FlingyData],
    data_type=scdata.FlingyData,
    kind=MemberKind.FLINGY,
):
    pass


class SpriteDataMember(
    SCDataObjectMember[scdata.SpriteData],
    data_type=scdata.SpriteData,
    kind=MemberKind.SPRITE,
):
    pass


class PlayerDataMember(
    SCDataObjectMember[scdata.PlayerData],
    data_type=scdata.PlayerData,
    kind=MemberKind.PLAYER,
):
    pass
