# Copyright 2019 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from abc import ABCMeta, abstractmethod
from typing import ClassVar, cast

from ... import core as c
from ... import utils as ut
from ...localize import _
from ...memio import muldiv4table


class EPDOffsetMap(ut.ExprProxy, metaclass=ABCMeta):
    __slots__ = ()
    _cast: ClassVar[bool] = False
    _update: ClassVar[
        dict[c.EUDVariable, tuple[c.Forward, c.Forward, c.Forward]]
    ] = {}
    _maxvalue: ClassVar[dict[c.EUDVariable, int]] = {}
    _stride_key: ClassVar[dict[c.EUDVariable, frozenset[int]]] = {}
    _stride_dict: ClassVar[
        dict[c.EUDVariable, dict[int, tuple[c.EUDVariable, c.EUDVariable | int]]]
    ] = {}

    @ut.classproperty
    @abstractmethod
    def range(self) -> tuple[int, int, int]:
        ...

    @classmethod
    def cast(cls, _from, **kwargs):
        if type(_from) is cls:
            return _from
        EPDOffsetMap._cast = True
        return cls(_from, **kwargs)

    def __init__(self, epd: int | c.EUDVariable) -> None:
        if isinstance(epd, c.EUDVariable) and not EPDOffsetMap._cast:
            epd = c.EUDVariable() << epd
            # To ellide var copy of rvalue variable (rvalue optimization),
            # variable is not added in dict to not increment refcount.
            #
            # example)
            # const foo = function (): TrgUnit { return 0; };
            # var x = foo();  // this should not copy variable.
            #
            # if epd not in EPDOffsetMap._update:
            #     EPDOffsetMap._update[epd] = (c.Forward(), c.Forward(), c.Forward())
            #     EPDOffsetMap._maxvalue[epd] = 0
            #     EPDOffsetMap._stride_key[epd] = frozenset(())
            #     EPDOffsetMap._stride_dict[epd] = {}
        EPDOffsetMap._cast = False
        super().__init__(epd)

    def _get_stride_cache(
        self, stride: int
    ) -> tuple[
        c.EUDVariable, int | c.EUDVariable, tuple[c.Forward, c.Forward, c.Forward]
    ]:
        value = self._value
        ut.ep_assert(isinstance(value, c.EUDVariable))
        # lazy calculate multiplication & division
        try:
            stride_dict = EPDOffsetMap._stride_dict[value]
        except KeyError:
            # See EPDOffsetMap.__init__
            stride_dict = {}
            maxvalue = (1 << type(self).range[1].bit_length()) - 1
            ut.ep_assert(maxvalue < 1024, _("Reference type can't have ArrayMember"))
            EPDOffsetMap._update[value] = (c.Forward(), c.Forward(), c.Forward())
            EPDOffsetMap._maxvalue[value] = maxvalue
            EPDOffsetMap._stride_key[value] = frozenset(())
            EPDOffsetMap._stride_dict[value] = stride_dict
        else:
            maxvalue = EPDOffsetMap._maxvalue[value]

        update_start, update_restore, update_end = EPDOffsetMap._update[value]
        if stride not in stride_dict or maxvalue < type(self).range[1]:
            q = c.EUDVariable()
            r: int | c.EUDVariable = 0 if stride % 4 == 0 else c.EUDVariable()
            stride_dict[stride] = (q, r)
            strides = frozenset(stride_dict.keys())
            EPDOffsetMap._stride_key[value] = strides
            bit_index = type(self).range[1].bit_length()
            maxvalue = (1 << bit_index) - 1
            EPDOffsetMap._maxvalue[value] = maxvalue

            derived_vars = []
            for stride in sorted(stride_dict.keys()):
                variables = stride_dict[stride]
                if stride % 4 == 0:
                    derived_vars.append(variables[0])
                else:
                    derived_vars.extend(variables)  # type: ignore[arg-type]

            update_start.Reset()
            update_restore.Reset()
            update_end.Reset()
            upd = muldiv4table._caller(bit_index - 1, strides)(value, *derived_vars)
            update_start << upd[0]
            update_restore << upd[1]
            varcount = muldiv4table.varcount_dict[strides]
            read_end = muldiv4table.muldiv_end_table[varcount]
            update_end << read_end
        else:
            q, r = stride_dict[stride]

        return q, r, (update_start, update_restore, update_end)

    def getepd(self, name: str) -> c.EUDVariable:
        from .memberimpl import CSpriteKind, CUnitKind, IscriptKind, PositionKind

        member = type(self).__dict__[name]
        kind = member.kind
        ut.ep_assert(kind.size() == 4, _("Only dword can be read as epd"))
        epd = member._get_epd(self)[0]
        if kind in (CUnitKind, CSpriteKind):
            return kind.read_epd(epd, 0)
        if kind in (PositionKind, IscriptKind):
            raise ut.EPError(_("Only dword can be read as epd"))

        from ...memio import f_epdread_epd

        return f_epdread_epd(epd)

    def getdwepd(self, name: str) -> tuple[c.EUDVariable, c.EUDVariable]:
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

        from ...memio import f_dwepdread_epd

        return f_dwepdread_epd(epd)

    def getpos(self, name: str) -> tuple[c.EUDVariable, c.EUDVariable]:
        from .memberimpl import CSpriteKind, CUnitKind, IscriptKind

        member = type(self).__dict__[name]
        kind = member.kind
        ut.ep_assert(kind.size() == 4, _("Only dword can be read as position"))
        if kind in (CUnitKind, CSpriteKind, IscriptKind):
            raise ut.EPError(_("Only dword can be read as position"))

        from ...memio import f_posread_epd

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


def _epd_cache(ptr: c.EUDVariable, ret=None) -> c.EUDVariable:
    epd = ret if ret else c.EUDVariable(0)
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


def _ptr_cache(epd: c.EUDVariable, ret=None) -> c.EUDVariable:
    ptr = ret if ret else c.EUDVariable(0)
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
