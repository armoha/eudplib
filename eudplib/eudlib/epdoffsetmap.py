#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2019 Armoha

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

from abc import ABCMeta
from collections.abc import Mapping
import enum
import traceback
from typing import cast, ClassVar, Final, Literal, TYPE_CHECKING

from .. import core as c
from .. import ctrlstru as cs
from .. import utils as ut
from ..localize import _
from .memiof import (
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
    f_epdcunitread_epd,
    f_epdread_epd,
    f_epdspriteread_epd,
    f_maskread_epd,
    f_maskwrite_epd,
    f_posread_epd,
    f_spriteepdread_epd,
    f_wadd_epd,
    f_wread_epd,
    f_wsubtract_epd,
    f_wwrite_epd,
)

if TYPE_CHECKING:
    from .cunit import CUnit


class MemberKind(enum.Enum):
    DWORD = enum.auto()
    WORD = enum.auto()
    BYTE = enum.auto()
    BOOL = enum.auto()
    C_UNIT = enum.auto()
    C_SPRITE = enum.auto()
    TRG_UNIT = enum.auto()
    TRG_PLAYER = enum.auto()
    ORDER = enum.auto()
    POSITION = enum.auto()
    POSITION_X = enum.auto()
    POSITION_Y = enum.auto()
    FLINGY = enum.auto()
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
            case MemberKind.ORDER:
                return c.EncodeUnitOrder(other)
            case MemberKind.FLINGY:
                return c.EncodeFlingy(other)
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

    def _read_func(self, epd, subp) -> c.EUDVariable:
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
                return f_maskread_epd(epd, 0x1FFF1FFF)
            case MemberKind.POSITION_X | MemberKind.POSITION_Y:
                return f_maskread_epd(epd, 0x1FFF << (8 * subp))
            case _:
                match self.size:
                    case 4:
                        return f_dwread_epd(epd)
                    case 2:
                        return f_wread_epd(epd, subp)
                    case 1:
                        return f_bread_epd(epd, subp)

    def _write_func(self, epd, subp, value) -> None:
        match self.size:
            case 4:
                f_dwwrite_epd(epd, value)
            case 2:
                f_wwrite_epd(epd, subp, value)
            case 1:
                f_bwrite_epd(epd, subp, value)

    def _add_func(self, epd, subp, value) -> None:
        match self.size:
            case 4:
                f_dwadd_epd(epd, value)
            case 2:
                f_wadd_epd(epd, subp, value)
            case 1:
                f_badd_epd(epd, subp, value)

    def _subtract_func(self, epd, subp, value) -> None:
        match self.size:
            case 4:
                f_dwsubtract_epd(epd, value)
            case 2:
                f_wsubtract_epd(epd, subp, value)
            case 1:
                f_bsubtract_epd(epd, subp, value)


class Member:
    name: Final[str]
    offset: Final[int]
    kind: Final[MemberKind]

    def __init__(self, name: str, offset: int, kind: MemberKind) -> None:
        self.name = name
        self.offset = offset
        self.kind = kind

    def read(self, epd) -> c.EUDVariable:
        q, r = divmod(self.offset, 4)
        return self.kind._read_func(epd + q, r)

    def write(self, epd, value) -> None:
        q, r = divmod(self.offset, 4)
        self.kind._write_func(epd + q, r, value)


def _checkEPDAddr(epd: object) -> None:
    u = ut.unProxy(epd)
    if isinstance(u, c.ConstExpr) and u.rlocmode != 1:
        ut.ep_warn(_("EPD check warning. Don't use raw pointer address"))
        traceback.print_stack()


class EPDOffsetMap(ut.ExprProxy, metaclass=ABCMeta):
    members: ClassVar[Mapping[str, Member]]

    def __init__(self, epd: int | c.EUDVariable) -> None:
        _checkEPDAddr(epd)
        self._epd: int | c.EUDVariable = epd
        super().__init__(epd)

    def getepd(self, name: str) -> "c.EUDVariable | CUnit":
        member = self.members[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as epd"))
        epd = self._epd + member.offset // 4
        match member.kind:
            case MemberKind.C_UNIT:
                return CUnit.from_read(epd)
            case MemberKind.C_SPRITE:
                return member.kind._read_func(epd, 0)
            case MemberKind.POSITION:
                raise ut.EPError(_("Only dword can be read as epd"))
            case _:
                return f_epdread_epd(epd)

    def getdwepd(self, name: str) -> tuple[c.EUDVariable, "c.EUDVariable | CUnit"]:
        member = self.members[name]
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
        member = self.members[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as position"))
        match member.kind:
            case MemberKind.C_UNIT | MemberKind.C_SPRITE:
                raise ut.EPError(_("Only dword can be read as position"))
            case _:
                return f_posread_epd(self._epd + member.offset // 4)

    def iaddattr(self, name: str, value) -> None:
        member = self.members[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        value = member.kind.cast(value)
        member.kind._add_func(epd, subp, value)

    # TODO: add operator for Subtract
    def isubtractattr(self, name: str, value) -> None:
        member = self.members[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        value = member.kind.cast(value)
        member.kind._subtract_func(epd, subp, value)

    def isubattr(self, name: str, value) -> None:
        member = self.members[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        value = member.kind.cast(value)
        member.kind._add_func(epd, subp, -value)

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
        member = self.members[name]
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
        member = self.members[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        mask = ((1 << (8 * member.kind.size)) - 1) << (8 * subp)
        value = member.kind.cast(value)
        if subp == 0:
            return c.MemoryXEPD(epd, c.AtMost, value, mask)
        else:
            return c.MemoryXEPD(epd, c.AtMost, c.f_bitlshift(value, 8 * subp), mask)

    def geattr(self, name, value):
        member = self.members[name]
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
