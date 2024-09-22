# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
from collections.abc import Iterator
from itertools import chain
from math import log2
from typing import ClassVar, NoReturn

from typing_extensions import Self

from ...localize import _
from ...utils import EPD, EPError, ExprProxy, ep_assert, unProxy
from .. import rawtrigger as bt
from ..allocator import ConstExpr, Forward, IsConstExpr
from ..curpl import GetCPCache
from ..inplacecw import iand, ilshift, ior, irshift, iset, isub, ixor
from ..variable import (
    EUDLightVariable,
    EUDVariable,
    IsEUDVariable,
    SeqCompute,
    SetVariables,
    VProc,
)
from ..variable.eudv import process_dest
from ..variable.vbuf import get_current_custom_varbuffer

cpcache: EUDVariable = GetCPCache()


class _EUDVArrayData(ConstExpr):
    def __new__(cls, *args, **kwargs) -> Self:
        return super().__new__(cls, None)

    def __init__(
        self,
        initvar: list[tuple[ConstExpr | int, ConstExpr | int, ConstExpr | int]],
    ) -> None:
        super().__init__()
        init = []
        for i, items in enumerate(initvar):
            dest, value, nextptr = items
            ep_assert(IsConstExpr(value), _("Invalid item #{}").format(repr(i)))
            init.append((0xFFFFFFFF, process_dest(dest), value, 0x072D0000, nextptr))
        self._init = init

    def Evaluate(self):  # noqa: N802
        evb = get_current_custom_varbuffer()
        if self not in evb._vdict:
            evb.create_vartriggers(self, self._init)

        return evb._vdict[self].Evaluate()


bt.PushTriggerScope()
_getter = bt.RawTrigger(nextptr=0, actions=bt.SetMemoryEPD(0, bt.SetTo, 0))
_getter_dst = EPD(_getter) + 86  # this and nextptr are set by __getitem__
_getter_val = EPD(_getter) + 87  # this is set by inner triggers of _EUDVArray

_lv = EUDLightVariable()
_convert_index = bt.SetMemoryEPD(0, bt.Add, 0)
_get_index = bt.RawTrigger(
    nextptr=0,
    actions=[_convert_index, bt.SetMemory(_convert_index + 20, bt.SetTo, 0)],
)
_index_for_get: list[bt.RawTrigger] = []
for i in range(28):
    _index_for_get.append(
        bt.RawTrigger(
            nextptr=_get_index if i == 0 else _index_for_get[i - 1],
            conditions=_lv.AtLeastX(1, 1 << i),
            actions=bt.SetMemory(_convert_index + 20, bt.Add, 72 << i),
        )
    )

_convert_index = bt.SetMemoryEPD(0, bt.SetTo, 0)
_set_index = bt.RawTrigger(nextptr=0, actions=_convert_index)
_index_for_set: list[bt.RawTrigger] = []
for i in range(28):
    _index_for_set.append(
        bt.RawTrigger(
            nextptr=_set_index if i == 0 else _index_for_set[i - 1],
            conditions=_lv.AtLeastX(1, 1 << i),
            actions=bt.SetMemory(_convert_index + 16, bt.Add, 18 << i),
        )
    )
bt.PopTriggerScope()


class _EUDVArray(ExprProxy):
    dont_flatten = True

    def __init__(
        self, initvar=None, *, _from=None, _size: int, _basetype: type | None
    ) -> None:
        ep_assert(0 <= _size < 2**28)
        self._size = _size
        self._basetype = _basetype

        # Initialization from value
        if _from is not None:
            baseobj = _from

        else:
            # Int -> interpret as sequence of 0s
            if initvar is None:
                initvar = [0] * _size

            if not isinstance(initvar[0], tuple):
                init = [(_getter_val, x, _getter) for x in initvar]
            else:
                init = initvar

            # For python iterables
            baseobj = _EUDVArrayData(init)

        super().__init__(baseobj)
        self._epd = EPD(self)

    def _bound_check(self, index: object) -> None:
        if isinstance(index, int) and not (0 <= index < self._size):
            e = _(
                "index out of bounds: the length of EUDVArray is {}"
                " but the index is {}"
            )
            raise EPError(e.format(self._size, index))

    def __getitem__(self, i):
        return self.get(i)

    def __setitem__(self, i, value) -> None:
        self.set(i, value)

    def get(self, i, **kwargs):
        ret = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
        try:
            dst = EPD(ret.getValueAddr())
        except AttributeError:
            dst = ret

        index = unProxy(i)
        self._bound_check(index)
        nexttrg = Forward()

        if isinstance(index, EUDVariable):
            size_msb = self._size.bit_length() - 1
            convert_start = _index_for_get[size_msb]
            _index_dst = _get_index + 344
            if IsEUDVariable(self._value):
                ep_assert(self._value is not index)
                # index copy to lv -> self.ptr -> _convert_index -> self
                bt.RawTrigger(
                    nextptr=index.GetVTable(),
                    actions=[
                        bt.SetNextPtr(index.GetVTable(), self._value.GetVTable()),
                        index.QueueAssignTo(_lv),
                        bt.SetNextPtr(self._value.GetVTable(), convert_start),
                        self._value.QueueAssignTo(EPD(_get_index) + 1),
                        bt.SetMemory(_index_dst, bt.SetTo, EPD(_get_index) + 1),
                        bt.SetNextPtr(_getter, nexttrg),
                        bt.SetMemoryEPD(_getter_dst, bt.SetTo, dst),
                    ],
                )
            else:
                # index copy to lv -> _convert_index -> self
                bt.RawTrigger(
                    nextptr=index.GetVTable(),
                    actions=[
                        bt.SetNextPtr(index.GetVTable(), convert_start),
                        index.QueueAssignTo(_lv),
                        bt.SetNextPtr(_get_index, self._value),
                        bt.SetMemory(_index_dst, bt.SetTo, EPD(_get_index) + 1),
                        bt.SetNextPtr(_getter, nexttrg),
                        bt.SetMemoryEPD(_getter_dst, bt.SetTo, dst),
                    ],
                )

        else:
            if IsEUDVariable(self._value):
                bt.RawTrigger(
                    nextptr=self._value.GetVTable(),
                    actions=[
                        bt.SetNextPtr(self._value.GetVTable(), 72 * index),
                        self._value.QueueAddTo(EPD(self._value.GetVTable()) + 1),
                        bt.SetNextPtr(_getter, nexttrg),
                        bt.SetMemoryEPD(_getter_dst, bt.SetTo, dst),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._value + 72 * index,
                    actions=[
                        bt.SetNextPtr(_getter, nexttrg),
                        bt.SetMemoryEPD(_getter_dst, bt.SetTo, dst),
                    ],
                )

        nexttrg << bt.NextTrigger()
        if self._basetype:
            ret = self._basetype.cast(ret)
        return ret

    def set(self, i, value, **kwargs):
        if self._basetype:
            value = self._basetype.cast(value)

        index = unProxy(i)
        self._bound_check(index)

        if all(not isinstance(v, EUDVariable) for v in (self._epd, index, value)):
            bt.RawTrigger(
                actions=bt.SetMemoryEPD(87 + self._epd + 18 * index, bt.SetTo, value)
            )
            return

        ep_assert(index is not value)

        # execution order: self._epd -> value -> index(->_convert_index)
        nexttrg = Forward()
        vv = []
        first_next_triggger = None

        writing_trigger = _set_index
        write_dest = _set_index + 344
        if isinstance(value, EUDVariable) and not isinstance(index, EUDVariable):
            writing_trigger = value.GetVTable()
            write_dest = value.getDestAddr()

        actions = [bt.SetNextPtr(writing_trigger, nexttrg)]

        for v in (self._epd, value, index):
            if isinstance(v, EUDVariable):
                vv.append(v)
                if first_next_triggger is None:
                    first_next_triggger = v.GetVTable()

        # nextptr
        for i in range(len(vv) - 1):
            actions.append(bt.SetNextPtr(vv[i].GetVTable(), vv[i + 1].GetVTable()))

        # dest
        const_dest = [87]
        if not isinstance(self._epd, EUDVariable):
            const_dest.append(self._epd)
        if not isinstance(index, EUDVariable):
            const_dest.append(18 * index)
        actions.append(bt.SetMemory(write_dest, bt.SetTo, sum(const_dest)))

        if isinstance(self._epd, EUDVariable):
            ep_assert(self._epd is not value)
            if len(vv) == 1:
                actions.append(bt.SetNextPtr(self._epd.GetVTable(), writing_trigger))
            actions.extend(self._epd.QueueAddTo(EPD(write_dest)))

        if isinstance(index, EUDVariable):
            size_msb = self._size.bit_length() - 1
            convert_start = _index_for_set[size_msb]
            actions.append(
                (
                    bt.SetNextPtr(index.GetVTable(), convert_start),
                    *index.QueueAssignTo(_lv),
                )
            )

        # value
        if isinstance(value, EUDVariable):
            if writing_trigger is value.GetVTable():
                actions.append(value.SetModifier(bt.SetTo))
            else:
                actions.extend(value.QueueAssignTo(EPD(_set_index) + 87))
        else:
            actions.append(bt.SetMemory(_set_index + 348, bt.SetTo, value))

        bt.RawTrigger(nextptr=first_next_triggger, actions=actions)
        nexttrg << bt.NextTrigger()


class EUDVArray:
    def __init__(self, size, basetype: type | None = None):
        self._size = size
        self._basetype = basetype

    def __call__(self, initvar=None, *, _from=None) -> _EUDVArray:
        return _EUDVArray(
            initvar=initvar,
            _from=_from,
            _size=self._size,
            _basetype=self._basetype,
        )

    def cast(self, _from):
        return self(_from=_from)


_index = EUDLightVariable()


class BitsTrg:
    cache: ClassVar[dict[str, dict[int | str, Forward]]] = {}

    def __init__(self, key: str) -> None:
        self._key: str = key

    def __bool__(self) -> bool:
        return self._key in BitsTrg.cache

    def __iter__(self) -> Iterator[dict[int | str, Forward]]:
        if not self:
            BitsTrg.cache[self._key] = {i: Forward() for i in range(28)}
            bt.PushTriggerScope()
            yield BitsTrg.cache[self._key]
            bt.PopTriggerScope()

    def __getitem__(self, index: int | str) -> Forward:
        return BitsTrg.cache[self._key][index]

    def __setitem__(self, index: int | str, item: Forward) -> None:
        BitsTrg.cache[self._key][index] = item


@functools.cache
def _InternalVArray(size: int, basetype: type | None = None):  # noqa: N802
    ep_assert(isinstance(size, int) and size < 2**28, "invalid size")

    def _bound_check(index: object) -> None:
        index = unProxy(unProxy)
        if not isinstance(index, int) or 0 <= index < size:
            return
        e = _(
            "index out of bounds: the length of EUDVArray is {}"
            " but the index is {}"
        )
        raise EPError(e.format(size, index))

    class _VArray(ExprProxy):
        dont_flatten = True

        def __init__(self, initvars=None, *, dest=0, nextptr=0, _from=None) -> None:
            # Initialization from value
            if _from is not None:
                baseobj = _from

            else:
                # Int -> interpret as sequence of 0s
                if initvars is None:
                    initvars = [0] * size

                # For python iterables
                baseobj = _EUDVArrayData([(dest, x, nextptr) for x in initvars])

            super().__init__(baseobj)
            self._epd = EPD(self)
            self._basetype = basetype

        def Assign(self, other) -> Self:  # noqa: N802
            if not isinstance(self._value, EUDVariable):
                raise EPError(
                    _("Can't assign {} to constant expression").format(other)
                )
            if isinstance(other, type(self)):
                SetVariables([self._value, self._epd], [other, other._epd])
            elif isinstance(other, int) and other == 0:
                SetVariables([self._value, self._epd], [0, 0])
            else:
                raise EPError(_("Can't assign {} to {}").format(other, self))
            return self

        def get(self, i, **kwargs):
            if IsEUDVariable(i):
                r = self._eudget(i, **kwargs)
            else:
                _bound_check(i)
                if IsEUDVariable(self):
                    r = self._get(i, **kwargs)
                else:
                    r = self._constget(i, **kwargs)

            if self._basetype:
                r = self._basetype.cast(r)
            return r

        def _eudget(self, i, **kwargs):
            bitstrg = BitsTrg("varrget")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=[
                            bt.SetMemory(trg["end"] + 4, bt.Add, 72 * (2**t)),
                            bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                            bt.SetMemory(trg["ret"] + 48, bt.Add, 18 * (2**t)),
                        ],
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        trg["ret"] << bt.SetDeaths(0, bt.SetTo, 0, 0),
                        bt.SetDeaths(0, bt.SetTo, 0, 0),
                    ],
                )

            r = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
            dst = EPD(r.getValueAddr()) if IsEUDVariable(r) else r
            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if not IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["end"] + 4, bt.SetTo, self),
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 86),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, dst),
                        bt.SetMemory(bitstrg["ret"] + 48, bt.SetTo, self._epd + 1),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, nptr),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            else:
                VProc(
                    [self, self._epd],
                    [
                        *self.QueueAssignTo(EPD(bitstrg["end"]) + 1),
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 86),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, dst),
                    ],
                )
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 48, bt.SetTo, 1),
                        self._epd.SetDest(EPD(bitstrg["ret"]) + 12),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, nptr),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            nptr << bt.NextTrigger()
            return r

        def _get(self, i, **kwargs):
            r = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
            dst = EPD(r.getValueAddr()) if IsEUDVariable(r) else r
            vtproc = Forward()
            nptr = Forward()
            a0, a2 = Forward(), Forward()

            VProc(
                [self, self._epd],
                [
                    bt.SetMemory(vtproc + 4, bt.SetTo, 72 * i),
                    *self.QueueAddTo(EPD(vtproc) + 1),
                    bt.SetMemory(a0 + 16, bt.SetTo, 18 * i + 344 // 4),
                    *self._epd.QueueAddTo(EPD(a0) + 4),
                ],
            )
            VProc(
                self._epd,
                [
                    a0 << bt.SetDeaths(0, bt.SetTo, dst, 0),
                    bt.SetMemory(a2 + 16, bt.SetTo, 18 * i + 1),
                    self._epd.SetDest(EPD(a2) + 4),
                ],
            )
            vtproc << bt.RawTrigger(
                nextptr=0,
                actions=[a2 << bt.SetDeaths(0, bt.SetTo, nptr, 0)],
            )

            nptr << bt.NextTrigger()
            return r

        def _constget(self, i, **kwargs):
            r = kwargs["ret"][0] if "ret" in kwargs else EUDVariable()
            dst = EPD(r.getValueAddr()) if IsEUDVariable(r) else r
            nptr = Forward()

            bt.RawTrigger(
                nextptr=self + 72 * i,
                actions=[
                    bt.SetDeaths(self._epd + 18 * i + 86, bt.SetTo, dst, 0),
                    bt.SetDeaths(self._epd + 18 * i + 1, bt.SetTo, nptr, 0),
                ],
            )
            nptr << bt.NextTrigger()
            return r

        def set(self, i, val) -> None:
            _bound_check(i)
            self._set(i, bt.SetTo, val)

        def _set(self, i, modifier, val) -> None:
            if not IsEUDVariable(i):
                iset(self._epd, 18 * i + 348 // 4, modifier, val)
                return
            modifier = bt.EncodeModifier(modifier) << 24

            bitstrg = BitsTrg("varrset")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[trg["ret"] << bt.SetDeaths(0, bt.SetTo, 0, 0)],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemoryX(
                            bitstrg["ret"] + 24, bt.SetTo, modifier, 0xFF << 24
                        ),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def fill(self, values, *, assert_expected_values_len=None) -> None:
            if assert_expected_values_len:
                ep_assert(len(values) == assert_expected_values_len)

            SeqCompute(
                [
                    (self._epd + (18 * i + 348 // 4), bt.SetTo, value)
                    for i, value in enumerate(values)
                ]
            )

        def __getitem__(self, i):
            return self.get(i)

        def __setitem__(self, i, value) -> None:
            self.set(i, value)

        def __iter__(self) -> NoReturn:
            # FIXME: add EUDVArray iterator
            raise EPError(_("Can't iterate EUDVArray"))

        def iadditem(self, i, val) -> None:
            _bound_check(i)
            self._set(i, bt.Add, val)

        # FIXME: add operator for Subtract
        def isubtractitem(self, i, val) -> None:
            _bound_check(i)
            self._set(i, bt.Subtract, val)

        def isubitem(self, i, val) -> None:
            _bound_check(i)
            if not IsEUDVariable(val):
                self._set(i, bt.Add, -val)
                return
            if not IsEUDVariable(i):
                isub(self._epd, 18 * i + 87, val)
                return
            bitstrg = BitsTrg("varrsub")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        bt.SetMemoryX(trg["ret"] + 20, bt.Add, -1, 0x55555555),
                        bt.SetMemoryX(trg["ret"] + 20, bt.Add, -1, 0xAAAAAAAA),
                        bt.SetMemory(trg["ret"] + 20, bt.Add, 1),
                        trg["ret"] << bt.SetDeaths(0, bt.Add, 0, 0),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        # defined when val is power of 2
        def imulitem(self, i, val) -> None:
            _bound_check(i)
            if not isinstance(val, int):
                raise AttributeError
            if val == 0:
                self.set(i, 0)
                return
            # val is power of 2
            if val & (val - 1) == 0:
                self.ilshiftitem(i, int(log2(val)))
                return
            # val is negation of power of 2
            if -val & (-val - 1) == 0:
                pass
            raise AttributeError

        # defined when val is power of 2
        def ifloordivitem(self, i, val) -> None:
            _bound_check(i)
            if not isinstance(val, int):
                raise AttributeError
            if val == 0:
                raise ZeroDivisionError
            # val is power of 2
            if val & (val - 1) == 0:
                self.irshiftitem(i, int(log2(val)))
                return
            # val is negation of power of 2
            if -val & (-val - 1) == 0:
                pass
            raise AttributeError

        # defined when val is power of 2
        def imoditem(self, i, val) -> None:
            _bound_check(i)
            if not isinstance(val, int):
                raise AttributeError
            if val == 0:
                raise ZeroDivisionError
            # val is power of 2
            if val & (val - 1) == 0:
                self.ianditem(i, val - 1)
                return
            raise AttributeError

        # FIXME: merge logic with EUDVariable and VariableBase

        def ilshiftitem(self, i, n) -> None:
            _bound_check(i)
            if not isinstance(n, int):
                raise AttributeError
            if not IsEUDVariable(i):
                ilshift(self._epd, 18 * i + 87, n)
                return
            if n == 0:
                return
            mask = (1 << (n + 1)) - 1
            bitstrg = BitsTrg(f"varrlshift{n}")
            cp = 13  # CurrentPlayer
            for trg in bitstrg:
                trg["end"] = Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(0x6509B0, bt.Add, 18 * (2**t)),
                    )

                def itemw(mod, value, mask):
                    return bt.SetMemoryXEPD(cp, mod, value, mask)

                trg["end"] << bt.RawTrigger(
                    nextptr=cpcache.GetVTable(),
                    actions=list(
                        chain(
                            *[
                                [
                                    itemw(bt.SetTo, 0, (mask >> 1) << (k + 1)),
                                    itemw(bt.Add, (mask >> 1) << k, mask << k),
                                ]
                                for k in reversed(range(32 - n))
                            ],
                            [
                                itemw(bt.SetTo, 0, mask >> 1),
                                cpcache.SetDest(EPD(0x6509B0)),
                            ],
                        )
                    ),
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def irshiftitem(self, i, n) -> None:
            _bound_check(i)
            if not isinstance(n, int):
                raise AttributeError
            if not IsEUDVariable(i):
                irshift(self._epd, 18 * i + 87, n)
                return
            if n == 0:
                return
            mask = (1 << (n + 1)) - 1
            bitstrg = BitsTrg(f"varrrshift{n}")
            cp = 13  # CurrentPlayer
            for trg in bitstrg:
                trg["end"] = Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(0x6509B0, bt.Add, 18 * (2**t)),
                    )

                def sub(value, mask):
                    return bt.SetMemoryXEPD(cp, bt.Subtract, value, mask)

                trg["end"] << bt.RawTrigger(
                    nextptr=cpcache.GetVTable(),
                    actions=[
                        bt.SetMemoryXEPD(cp, bt.SetTo, 0, mask >> 1),
                        cpcache.SetDest(EPD(0x6509B0)),
                    ]
                    + [sub((mask >> 1) << k, mask << k) for k in range(32 - n)],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def ipowitem(self, i, val) -> None:
            _bound_check(i)
            if isinstance(val, int) and val == 1:
                return
            raise AttributeError

        def ianditem(self, i, val) -> None:
            _bound_check(i)
            if not IsEUDVariable(i):
                iand(self._epd, 18 * i + 87, val)
                return
            bitstrg = BitsTrg("varrand")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[
                        bt.SetMemoryX(trg["ret"], bt.Add, -1, 0x55555555),
                        bt.SetMemoryX(trg["ret"], bt.Add, -1, 0xAAAAAAAA),
                        trg["ret"] << bt.SetMemoryXEPD(0, bt.SetTo, 0, 0),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        *val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        *val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def ioritem(self, i, val) -> None:
            _bound_check(i)
            if not IsEUDVariable(i):
                ior(self._epd, 18 * i + 87, val)
                return
            bitstrg = BitsTrg("varror")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(trg["ret"] + 16, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=0,
                    actions=[trg["ret"] << bt.SetMemoryXEPD(0, bt.SetTo, ~0, 0)],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr = Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        *val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(bitstrg["ret"]) + 4),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            elif IsEUDVariable(val):
                bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        *val.QueueAssignTo(EPD(bitstrg["ret"])),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=i.GetVTable(),
                    actions=[
                        bt.SetMemory(bitstrg["ret"] + 16, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"], bt.SetTo, val),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(bitstrg["end"], nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        def ixoritem(self, i, val) -> None:
            _bound_check(i)
            if not IsEUDVariable(i):
                ixor(self._epd, 18 * i + 87, val)
                return
            bitstrg = BitsTrg("varrxor")
            for trg in bitstrg:
                trg["end"], trg["ret"] = Forward(), Forward()
                for t in range(27, -1, -1):
                    trg[t] << bt.RawTrigger(
                        conditions=_index.AtLeastX(1, 2**t),
                        actions=bt.SetMemory(0x6509B0, bt.Add, 18 * (2**t)),
                    )
                trg["end"] << bt.RawTrigger(
                    nextptr=cpcache.GetVTable(),
                    actions=[
                        trg["ret"]
                        << bt.SetDeathsX(
                            13, bt.Add, 0, 0, 0x55555555
                        ),  # CurrentPlayer
                        bt.SetDeathsX(13, bt.Add, 0, 0, 0xAAAAAAAA),  # CurrentPlayer
                        cpcache.SetDest(EPD(0x6509B0)),
                    ],
                )

            bits = max((size - 1).bit_length() - 1, 0)
            nptr, trg1, trg2 = Forward(), Forward(), Forward()
            if IsEUDVariable(self._epd) and IsEUDVariable(val):
                trg1 << bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), val.GetVTable()),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), trg2),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
                trg2 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        val.SetDest(EPD(bitstrg["ret"]) + 13),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            elif IsEUDVariable(self._epd):
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, 87),
                        *self._epd.QueueAddTo(EPD(0x6509B0)),
                        bt.SetNextPtr(self._epd.GetVTable(), i.GetVTable()),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, val),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
            elif IsEUDVariable(val):
                trg1 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), trg2),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
                trg2 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        val.SetDest(EPD(bitstrg["ret"]) + 13),
                        bt.SetNextPtr(val.GetVTable(), i.GetVTable()),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        bt.SetMemory(bitstrg["ret"] + 20, bt.SetTo, val),
                        bt.SetMemory(bitstrg["ret"] + 52, bt.SetTo, val),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(cpcache.GetVTable(), nptr),
                    ],
                )
            nptr << bt.NextTrigger()

        # FIXME: Add operator?
        def iinvertitem(self, i) -> None:
            _bound_check(i)
            self.ixoritem(i, 0xFFFFFFFF)
            return

        def inotitem(self, i) -> NoReturn:
            _bound_check(i)
            raise AttributeError

        # item comparisons
        def eqitem(self, i, val) -> bt.Condition:
            _bound_check(i)
            if not IsEUDVariable(i):
                return bt.MemoryEPD(self._epd + (18 * i + 87), bt.Exactly, val)
            raise AttributeError

        def neitem(self, i, val):
            _bound_check(i)
            if not IsEUDVariable(i):
                from ...ctrlstru import EUDNot

                return EUDNot(
                    bt.MemoryEPD(self._epd + (18 * i + 87), bt.Exactly, val)
                )
            raise AttributeError

        def leitem(self, i, val) -> bt.Condition:
            _bound_check(i)
            if not IsEUDVariable(i):
                return bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtMost, val)
            raise AttributeError

        def geitem(self, i, val) -> bt.Condition:
            _bound_check(i)
            if not IsEUDVariable(i):
                return bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtLeast, val)
            raise AttributeError

        def ltitem(self, i, val):
            _bound_check(i)
            if not IsEUDVariable(i):
                from ...ctrlstru import EUDNot

                return EUDNot(
                    bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtLeast, val)
                )
            raise AttributeError

        def gtitem(self, i, val):
            _bound_check(i)
            if not IsEUDVariable(i):
                from ...ctrlstru import EUDNot

                return EUDNot(
                    bt.MemoryEPD(self._epd + (18 * i + 87), bt.AtMost, val)
                )
            raise AttributeError

    return _VArray
