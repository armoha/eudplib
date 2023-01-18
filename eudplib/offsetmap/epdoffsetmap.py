#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from abc import ABCMeta, abstractmethod
from collections.abc import Mapping
import enum
from typing import cast, ClassVar, Final, Literal, NoReturn, TypeAlias, TypeVar, TYPE_CHECKING

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from ..eudlib.memiof import (
    f_badd_epd,
    f_bread_epd,
    f_bsubtract_epd,
    f_bwrite_epd,
    f_cunitepdread_epd,
    f_dwadd_epd,
    f_dwepdread_epd,
    f_dwread_epd,
    f_dwsubtract_epd,
    f_dwwrite_epd,
    f_epdread_epd,
    f_epdspriteread_epd,
    f_maskread_epd,
    f_posread_epd,
    f_spriteepdread_epd,
    f_wadd_epd,
    f_wread_epd,
    f_wsubtract_epd,
    f_wwrite_epd,
)
from ..eudlib.memiof.memifgen import _mapXYmask

if TYPE_CHECKING:
    from .cunit import CUnit


class MemberKind(enum.Enum):
    # FIXME: __slots__ = ()
    DWORD = enum.auto()
    WORD = enum.auto()
    BYTE = enum.auto()
    BOOL = enum.auto()
    C_UNIT = enum.auto()
    C_SPRITE = enum.auto()
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

    def cast(self, other):
        match self:
            case MemberKind.DWORD | MemberKind.WORD | MemberKind.BYTE | MemberKind.BOOL | MemberKind.C_UNIT | MemberKind.C_SPRITE | MemberKind.POSITION | MemberKind.POSITION_X | MemberKind.POSITION_Y:
                return other
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

    @property
    def size(self) -> Literal[1, 2, 4]:
        match self:
            case MemberKind.DWORD | MemberKind.C_UNIT | MemberKind.C_SPRITE | MemberKind.POSITION:
                return 4
            case MemberKind.WORD | MemberKind.POSITION_X | MemberKind.POSITION_Y | MemberKind.FLINGY | MemberKind.TRG_UNIT:
                return 2
            case _:
                return 1

    def read_epd(self, epd, subp) -> c.EUDVariable:
        match self:
            case MemberKind.BOOL:
                return f_maskread_epd(epd, 1 << (8 * subp))
            case MemberKind.C_UNIT:
                return f_cunitepdread_epd(epd)
            case MemberKind.C_SPRITE:
                return f_epdspriteread_epd(epd)
            case MemberKind.TRG_UNIT | MemberKind.FLINGY:
                return f_bread_epd(epd, subp)
            case MemberKind.POSITION:
                return f_maskread_epd(epd, (lambda x, y: x + 65536 * y)(*_mapXYmask()))
            case MemberKind.POSITION_X:
                return f_maskread_epd(epd, _mapXYmask()[0] << (8 * subp))
            case MemberKind.POSITION_Y:
                return f_maskread_epd(epd, _mapXYmask()[1] << (8 * subp))
            case _:
                match self.size:
                    case 4:
                        return f_dwread_epd(epd)
                    case 2:
                        return f_wread_epd(epd, subp)
                    case 1:
                        return f_bread_epd(epd, subp)

    def write_epd(self, epd, subp, value) -> None:
        match self.size:
            case 4:
                f_dwwrite_epd(epd, value)
            case 2:
                f_wwrite_epd(epd, subp, value)
            case 1:
                f_bwrite_epd(epd, subp, value)

    def add_epd(self, epd, subp, value) -> None:
        match self.size:
            case 4:
                f_dwadd_epd(epd, value)
            case 2:
                f_wadd_epd(epd, subp, value)
            case 1:
                f_badd_epd(epd, subp, value)

    def subtract_epd(self, epd, subp, value) -> None:
        match self.size:
            case 4:
                f_dwsubtract_epd(epd, value)
            case 2:
                f_wsubtract_epd(epd, subp, value)
            case 1:
                f_bsubtract_epd(epd, subp, value)


class BaseMember(metaclass=ABCMeta):
    """Base descriptor class for EPDOffsetMap"""

    __slots__ = ("offset", "kind")

    offset: Final[int]
    kind: Final[MemberKind]

    def __init__(self, offset: int, kind: MemberKind) -> None:
        self.offset = offset
        self.kind = kind

    @abstractmethod
    def __get__(self, instance, owner=None):
        ...

    @abstractmethod
    def __set__(self, instance, value) -> None:
        ...


class UnsupportedMember(BaseMember):
    """Not supported EUD"""

    __slots__ = "name"

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None) -> NoReturn:
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))

    def __set__(self, instance, value) -> NoReturn:
        raise ut.EPError(_("Unsupported EUD: {}").format(self.name))


class Member(BaseMember):
    """Descriptor for EPDOffsetMap"""

    __slots__ = ()

    def __get__(self, instance, owner=None) -> c.EUDVariable:
        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            return self.kind.read_epd(instance._epd + q, r)
        raise AttributeError

    def __set__(self, instance, value) -> None:
        q, r = divmod(self.offset, 4)
        if isinstance(instance, EPDOffsetMap):
            value = self.kind.cast(value)
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


class CUnitMember(BaseMember):
    """Descriptor for EPDOffsetMap"""

    __slots__ = ()

    def __init__(self, offset: int) -> None:
        super().__init__(offset, MemberKind.C_UNIT)

    def __get__(self, instance, owner=None) -> "CUnit":
        from .cunit import CUnit

        if isinstance(instance, EPDOffsetMap):
            return CUnit.from_read(instance._epd + self.offset // 4)
        raise AttributeError

    def __set__(self, instance, value) -> None:
        from .cunit import CUnit

        q, r = divmod(self.offset, 4)
        if isinstance(value, CUnit):
            value = value.ptr
        if isinstance(instance, EPDOffsetMap):
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


class CSpriteMember(BaseMember):
    """Descriptor for EPDOffsetMap"""

    __slots__ = ()

    def __init__(self, offset: int) -> None:
        super().__init__(offset, MemberKind.C_SPRITE)

    def __get__(self, instance, owner=None) -> "CSprite":
        if isinstance(instance, EPDOffsetMap):
            return CSprite.from_read(instance._epd + self.offset // 4)
        raise AttributeError

    def __set__(self, instance, value) -> None:
        q, r = divmod(self.offset, 4)
        if isinstance(value, CSprite):
            value = value.ptr
        if isinstance(instance, EPDOffsetMap):
            self.kind.write_epd(instance._epd + q, r, value)
            return
        raise AttributeError


def _checkEPDAddr(epd: object) -> None:
    u = ut.unProxy(epd)
    if isinstance(u, c.ConstExpr) and u.rlocmode != 1:
        raise ut.EPError(_("EPD check warning. Don't use raw pointer address"))


class EPDOffsetMap(ut.ExprProxy, metaclass=ABCMeta):
    __slots__ = "_epd"

    def __init__(self, epd: int | c.EUDVariable) -> None:
        self._epd: int | c.EUDVariable = epd
        super().__init__(epd)

    def getepd(self, name: str) -> "c.EUDVariable | CUnit":
        member = type(self).__dict__[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as epd"))
        epd = self._epd + member.offset // 4
        match member.kind:
            case MemberKind.C_UNIT:
                return CUnit.from_read(epd)
            case MemberKind.C_SPRITE:
                return member.kind.read_epd(epd, 0)
            case MemberKind.POSITION:
                raise ut.EPError(_("Only dword can be read as epd"))
            case _:
                return f_epdread_epd(epd)

    def getdwepd(self, name: str) -> tuple[c.EUDVariable, "c.EUDVariable | CUnit"]:
        member = type(self).__dict__[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as epd"))
        epd = self._epd + member.offset // 4
        match member.kind:
            case MemberKind.C_UNIT:
                cunit = CUnit.from_read(epd)
                return cast(c.EUDVariable, cunit._ptr), cunit
            case MemberKind.C_SPRITE:
                return f_spriteepdread_epd(epd)
            case MemberKind.POSITION:
                raise ut.EPError(_("Only dword can be read as epd"))
            case _:
                return f_dwepdread_epd(epd)

    def getpos(self, name: str) -> tuple[c.EUDVariable, c.EUDVariable]:
        member = type(self).__dict__[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as position"))
        match member.kind:
            case MemberKind.C_UNIT | MemberKind.C_SPRITE:
                raise ut.EPError(_("Only dword can be read as position"))
            case _:
                return f_posread_epd(self._epd + member.offset // 4)

    def iaddattr(self, name: str, value) -> None:
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        value = member.kind.cast(value)
        member.kind.add_epd(epd, subp, value)

    # TODO: add operator for Subtract
    def isubtractattr(self, name: str, value) -> None:
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        value = member.kind.cast(value)
        member.kind.subtract_epd(epd, subp, value)

    def isubattr(self, name: str, value) -> None:
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        value = member.kind.cast(value)
        member.kind.add_epd(epd, subp, -value)

    def imulattr(self, name, value):
        raise AttributeError

    def ifloordivattr(self, name, value):
        raise AttributeError

    def imodattr(self, name, value):
        raise AttributeError

    def ilshiftattr(self, name, value):
        raise AttributeError

    def irshiftattr(self, name, value):
        raise AttributeError

    def ipowattr(self, name, value):
        raise AttributeError

    def iandattr(self, name, value):
        raise AttributeError

    def iorattr(self, name, value):
        raise AttributeError

    def ixorattr(self, name, value):
        raise AttributeError

    # FIXME: Add operator for x[i] = ~x[i]
    def iinvertattr(self, name, value):
        raise AttributeError

    # Attribute comparisons

    def eqattr(self, name: str, value):
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        mask = ((1 << (8 * member.kind.size)) - 1) << (8 * subp)
        value = member.kind.cast(value)
        if subp == 0:
            return c.MemoryXEPD(epd, c.Exactly, value, mask)
        else:
            return c.MemoryXEPD(epd, c.Exactly, c.f_bitlshift(value, 8 * subp), mask)

    def neattr(self, name, value):
        raise AttributeError

    def leattr(self, name, value):
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        mask = ((1 << (8 * member.kind.size)) - 1) << (8 * subp)
        value = member.kind.cast(value)
        if subp == 0:
            return c.MemoryXEPD(epd, c.AtMost, value, mask)
        else:
            return c.MemoryXEPD(epd, c.AtMost, c.f_bitlshift(value, 8 * subp), mask)

    def geattr(self, name, value):
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        mask = ((1 << (8 * member.kind.size)) - 1) << (8 * subp)
        value = member.kind.cast(value)
        if subp == 0:
            return c.MemoryXEPD(epd, c.AtLeast, value, mask)
        else:
            return c.MemoryXEPD(epd, c.AtLeast, c.f_bitlshift(value, 8 * subp), mask)

    def ltattr(self, name, value):
        raise AttributeError

    def gtattr(self, name, value):
        raise AttributeError


c.PushTriggerScope()
_epdcache = c.NextTrigger()
_epdcache_ptr = c.EUDVariable()
_epdcache_epd = ut.EPD(_epdcache_ptr)
c.RawTrigger(
    nextptr=_epdcache_epd.GetVTable(),
    conditions=_epdcache_ptr.Exactly(0),
    actions=_epdcache_epd.SetNumber(0),
)
c.PopTriggerScope()

c.PushTriggerScope()
_ptrcache = c.NextTrigger()
_ptrcache_epd = c.EUDVariable()
_ptrcache_ptr = _ptrcache_epd * 4
_ptrcache_ptr += 0x58A364
c.RawTrigger(
    nextptr=_ptrcache_ptr.GetVTable(),
    conditions=_ptrcache_epd.Exactly(0),
    actions=_ptrcache_ptr.SetNumber(0),
)
c.PopTriggerScope()


def EPDCache(ptr: c.EUDVariable) -> c.EUDVariable:
    epd = c.EUDVariable(0)
    is_ptr_equal = ptr.Exactly(0)
    check, update, skip, end = [c.Forward() for _ in range(4)]
    check << c.RawTrigger(
        nextptr=update, conditions=is_ptr_equal, actions=c.SetNextPtr(check, skip)
    )
    update << c.VProc(
        ptr,
        [
            ptr.QueueAssignTo(_epdcache_ptr),
            _epdcache_epd.SetDest(epd),
            c.SetNextPtr(_epdcache_epd.GetVTable(), end),
        ],
    )
    c.SetNextTrigger(_epdcache)
    skip << c.RawTrigger(actions=c.SetNextPtr(check, update))
    end << c.NextTrigger()
    return epd


def PtrCache(epd: c.EUDVariable) -> c.EUDVariable:
    ptr = c.EUDVariable()
    is_epd_equal = epd.Exactly(0)
    check, update, skip, end = [c.Forward() for _ in range(4)]
    check << c.RawTrigger(
        nextptr=update, conditions=is_epd_equal, actions=c.SetNextPtr(check, skip)
    )
    update << c.VProc(
        epd,
        [
            epd.QueueAssignTo(_ptrcache_epd),
            _ptrcache_ptr.SetDest(ptr),
            c.SetNextPtr(_ptrcache_ptr.GetVTable(), end),
        ],
    )
    c.SetNextTrigger(_ptrcache)
    skip << c.RawTrigger(actions=c.SetNextPtr(check, update))
    end << c.NextTrigger()
    return ptr


T = TypeVar("T", bound="CSprite")
int_or_var: TypeAlias = int | c.EUDVariable | ut.ExprProxy


class CSprite(EPDOffsetMap):
    __slots__ = "_ptr"

    prev = CSpriteMember(0x00)
    next = CSpriteMember(0x04)
    sprite = Member(0x08, MemberKind.SPRITE)
    playerID = Member(0x0A, MemberKind.TRG_PLAYER)  # officially "creator"
    # 0 <= selectionIndex <= 11. Index in the selection area at bottom of screen.
    selectionIndex = Member(0x0B, MemberKind.BYTE)
    # Player bits indicating the visibility for a player (not hidden by the fog-of-war)
    visibilityFlags = Member(0x0C, MemberKind.BYTE)
    elevationLevel = Member(0x0D, MemberKind.BYTE)
    # 0x01  Draw selection circle.
    # 0x02  Ally selection?
    # 0x04  Ally selection?
    # 0x08  Draw HP bar, Selected
    # 0x10
    # 0x20  Hidden
    # 0x40  Burrowed
    # 0x80  Iscript unbreakable code section.
    flags = Member(0x0E, MemberKind.BYTE)
    selectionTimer = Member(0x0F, MemberKind.BYTE)
    index = Member(0x10, MemberKind.WORD)
    unknown0x12 = Member(0x12, MemberKind.BYTE)
    unknown0x13 = Member(0x13, MemberKind.BYTE)
    pos = Member(0x14, MemberKind.POSITION)
    posX = Member(0x14, MemberKind.POSITION_X)
    posY = Member(0x16, MemberKind.POSITION_Y)
    mainGraphic = Member(0x18, MemberKind.DWORD)  # officially "pImagePrimary"
    imageHead = Member(0x1C, MemberKind.DWORD)
    imageTail = Member(0x20, MemberKind.DWORD)

    def __init__(self, epd: int_or_var, *, ptr: int_or_var | None = None) -> None:
        """EPD Constructor of CSprite. Use CSprite.from_ptr(ptr) for ptr value"""
        _epd: int | c.EUDVariable
        self._ptr: int | c.EUDVariable | None

        if isinstance(epd, CSprite):
            _epd, self._ptr = epd._epd, epd._ptr
        else:
            u, p = ut.unProxy(epd), ut.unProxy(ptr)
            if isinstance(u, int):
                if p is not None and not isinstance(p, int):
                    raise ut.EPError(_("Invalid input for CSprite: {}").format((epd, ptr)))
                q, r = divmod(u - ut.EPD(0x59CCA8), 84)  # check epd
                if r == 0 and 0 <= q < 1700:
                    _epd, self._ptr = u, 0x59CCA8 + 336 * q
                else:
                    raise ut.EPError(_("Invalid input for CSprite: {}").format((epd, ptr)))
            elif isinstance(u, c.EUDVariable):
                if p is not None and not isinstance(p, c.EUDVariable):
                    raise ut.EPError(_("Invalid input for CSprite: {}").format((epd, ptr)))
                _epd, self._ptr = u, p
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
                raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format(ptr))
        elif isinstance(u, c.EUDVariable):
            epd = EPDCache(u)
        else:
            raise ut.EPError(_("Invalid input for EPDCUnitMap: {}").format(epd))

        return cls(epd, ptr=u)

    @classmethod
    def from_read(cls: type[T], epd) -> T:
        _ptr, _epd = f_spriteepdread_epd(epd)
        return cls(_epd, ptr=_ptr)

    @property
    def ptr(self) -> int | c.EUDVariable:
        if self._ptr is not None:
            return self._ptr
        return PtrCache(cast(c.EUDVariable, self._epd))
