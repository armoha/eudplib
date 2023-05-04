#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta
from typing import TYPE_CHECKING, cast

from .. import core as c
from .. import utils as ut
from ..localize import _
from .member import MemberKind

if TYPE_CHECKING:
    from .csprite import CSprite
    from .cunit import CUnit


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
                from .cunit import CUnit

                return CUnit.from_read(epd)
            case MemberKind.C_SPRITE:
                return member.kind.read_epd(epd, 0)
            case MemberKind.POSITION:
                raise ut.EPError(_("Only dword can be read as epd"))
            case _:
                from ..eudlib.memiof import f_epdread_epd

                return f_epdread_epd(epd)

    def getdwepd(
        self, name: str
    ) -> tuple[c.EUDVariable, "c.EUDVariable | CUnit | CSprite"]:
        member = type(self).__dict__[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as epd"))
        epd = self._epd + member.offset // 4
        match member.kind:
            case MemberKind.C_UNIT:
                from .cunit import CUnit

                cunit = CUnit.from_read(epd)
                return cast(c.EUDVariable, cunit._ptr), cunit
            case MemberKind.C_SPRITE:
                from .csprite import CSprite

                csprite = CSprite.from_read(epd)
                return cast(c.EUDVariable, csprite._ptr), csprite
            case MemberKind.POSITION:
                raise ut.EPError(_("Only dword can be read as epd"))
            case _:
                from ..eudlib.memiof import f_dwepdread_epd

                return f_dwepdread_epd(epd)

    def getpos(self, name: str) -> tuple[c.EUDVariable, c.EUDVariable]:
        member = type(self).__dict__[name]
        ut.ep_assert(member.kind.size == 4, _("Only dword can be read as position"))
        match member.kind:
            case MemberKind.C_UNIT | MemberKind.C_SPRITE:
                raise ut.EPError(_("Only dword can be read as position"))
            case _:
                from ..eudlib.memiof import f_posread_epd

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
        if subp != 0:
            value = c.f_bitlshift(value, 8 * subp)
        if isinstance(value, int) and value & ~mask:
            raise ut.EPError(
                _("{} is out of range({}) for {} Member {}").format(
                    value, mask, type(self), name
                )
            )
        return c.MemoryXEPD(epd, c.Exactly, value, mask)

    def neattr(self, name, value):
        raise AttributeError

    def leattr(self, name, value):
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        mask = ((1 << (8 * member.kind.size)) - 1) << (8 * subp)
        value = member.kind.cast(value)
        if subp != 0:
            value = c.f_bitlshift(value, 8 * subp)
        if isinstance(value, int) and value & ~mask:
            raise ut.EPError(
                _("{} is out of range({}) for {} Member {}").format(
                    value, mask, type(self), name
                )
            )
        return c.MemoryXEPD(epd, c.AtMost, value, mask)

    def geattr(self, name, value):
        member = type(self).__dict__[name]
        offsetEPD, subp = divmod(member.offset, 4)
        epd = self._epd + offsetEPD
        mask = ((1 << (8 * member.kind.size)) - 1) << (8 * subp)
        value = member.kind.cast(value)
        if subp != 0:
            value = c.f_bitlshift(value, 8 * subp)
        if isinstance(value, int) and value & ~mask:
            raise ut.EPError(
                _("{} is out of range({}) for {} Member {}").format(
                    value, mask, type(self), name
                )
            )
        return c.MemoryXEPD(epd, c.AtLeast, value, mask)

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
