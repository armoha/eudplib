#!/usr/bin/python
# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta
from typing import TYPE_CHECKING, ClassVar, cast

from .. import core as c
from .. import utils as ut
from ..localize import _

if TYPE_CHECKING:
    from .csprite import CSprite
    from .cunit import CUnit


class EPDOffsetMap(ut.ExprProxy, metaclass=ABCMeta):
    __slots__ = ("_epd",)
    _cast: ClassVar[bool] = False

    @classmethod
    def cast(cls, other, **kwargs):
        if isinstance(other, cls):
            return other
        EPDOffsetMap._cast = True
        return cls(other, **kwargs)

    def __init__(self, epd: int | c.EUDVariable) -> None:
        self._epd: int | c.EUDVariable = epd
        if isinstance(epd, c.EUDVariable) and not EPDOffsetMap._cast:
            source = epd
            epd = c.EUDVariable()
            epd << source
        EPDOffsetMap._cast = False
        super().__init__(epd)

    def getepd(self, name: str) -> "c.EUDVariable | CUnit":
        from .memberimpl import CSpriteKind, CUnitKind, IscriptKind, PositionKind

        member = type(self).__dict__[name]
        kind = member.kind
        ut.ep_assert(kind.size() == 4, _("Only dword can be read as epd"))
        epd = member._get_epd(self)[0]
        if kind in (CUnitKind, CSpriteKind):
            return kind.read_epd(epd, 0)
        if kind in (PositionKind, IscriptKind):
            raise ut.EPError(_("Only dword can be read as epd"))

        from ..memio import f_epdread_epd

        return f_epdread_epd(epd)

    def getdwepd(
        self, name: str
    ) -> tuple[c.EUDVariable, "c.EUDVariable | CUnit | CSprite"]:
        from .memberimpl import CSpriteKind, CUnitKind, IscriptKind, PositionKind

        member = type(self).__dict__[name]
        kind = member.kind
        ut.ep_assert(kind.size() == 4, _("Only dword can be read as epd"))
        epd = member._get_epd(self)[0]
        if kind in (CUnitKind, CSpriteKind):
            cinstance = kind.read_epd(epd, 0)
            return cast(c.EUDVariable, cinstance._ptr), cinstance
        if kind in (PositionKind, IscriptKind):
            raise ut.EPError(_("Only dword can be read as epd"))

        from ..memio import f_dwepdread_epd

        return f_dwepdread_epd(epd)

    def getpos(self, name: str) -> tuple[c.EUDVariable, c.EUDVariable]:
        from .memberimpl import CSpriteKind, CUnitKind, IscriptKind

        member = type(self).__dict__[name]
        kind = member.kind
        ut.ep_assert(kind.size() == 4, _("Only dword can be read as position"))
        if kind in (CUnitKind, CSpriteKind, IscriptKind):
            raise ut.EPError(_("Only dword can be read as position"))

        from ..memio import f_posread_epd

        return f_posread_epd(member._get_epd(self)[0])

    def iaddattr(self, name: str, value) -> None:
        member = type(self).__dict__[name]
        epd, subp = member._get_epd(self)
        member.kind.add_epd(epd, subp, member.kind.cast(value))

    # TODO: add operator for Subtract
    def isubtractattr(self, name: str, value) -> None:
        member = type(self).__dict__[name]
        epd, subp = member._get_epd(self)
        member.kind.subtract_epd(epd, subp, member.kind.cast(value))

    def isubattr(self, name: str, value) -> None:
        member = type(self).__dict__[name]
        epd, subp = member._get_epd(self)
        value = member.kind.cast(value)
        member.kind.add_epd(epd, subp, -member.kind.cast(value))

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
        epd, subp = member._get_epd(self)
        mask = ((1 << (8 * member.kind.size())) - 1) << (8 * subp)
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
        epd, subp = member._get_epd(self)
        mask = ((1 << (8 * member.kind.size())) - 1) << (8 * subp)
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
        epd, subp = member._get_epd(self)
        mask = ((1 << (8 * member.kind.size())) - 1) << (8 * subp)
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


def _epd_cache(ptr: c.EUDVariable) -> c.EUDVariable:
    epd = c.EUDVariable(0)
    is_ptr_equal = ptr.Exactly(0)
    check, update, skip, end = (c.Forward() for _ in range(4))
    check << c.RawTrigger(
        nextptr=update, conditions=is_ptr_equal, actions=c.SetNextPtr(check, skip)
    )
    update << c.VProc(
        [ptr, _epdcache_ptr],
        [
            ptr.QueueAssignTo(_epdcache_ptr),
            _epdcache_ptr.SetDest(ut.EPD(is_ptr_equal) + 2),
            _epdcache_epd.SetDest(epd),
            c.SetNextPtr(_epdcache_epd.GetVTable(), end),
        ],
    )
    c.SetNextTrigger(_epdcache)
    skip << c.RawTrigger(actions=c.SetNextPtr(check, update))
    end << c.NextTrigger()
    return epd


def _ptr_cache(epd: c.EUDVariable) -> c.EUDVariable:
    ptr = c.EUDVariable(0)
    is_epd_equal = epd.Exactly(0)
    check, update, skip, end = (c.Forward() for _ in range(4))
    check << c.RawTrigger(
        nextptr=update, conditions=is_epd_equal, actions=c.SetNextPtr(check, skip)
    )
    update << c.VProc(
        [epd, _ptrcache_epd],
        [
            epd.QueueAssignTo(_ptrcache_epd),
            _ptrcache_epd.SetDest(ut.EPD(is_epd_equal) + 2),
            _ptrcache_ptr.SetDest(ptr),
            c.SetNextPtr(_ptrcache_ptr.GetVTable(), end),
        ],
    )
    c.SetNextTrigger(_ptrcache)
    skip << c.RawTrigger(actions=c.SetNextPtr(check, update))
    end << c.NextTrigger()
    return ptr
