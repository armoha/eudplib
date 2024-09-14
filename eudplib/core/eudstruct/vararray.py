# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

import functools
from collections.abc import Iterator
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
    VProc,
)
from ..variable.eudv import process_dest
from ..variable.vbuf import (
    get_current_custom_varbuffer,
    get_current_varbuffer,
)


@functools.cache
def eudvarray_data(size):
    ep_assert(isinstance(size, int) and size < 2**28, "invalid size")

    class _EUDVArrayData(ConstExpr):
        def __new__(cls, *args, **kwargs) -> Self:
            return super().__new__(cls, None)

        def __init__(self, initvars, *, dest=0, nextptr=0) -> None:
            super().__init__()
            ep_assert(
                len(initvars) == size,
                _("{} items expected, got {}").format(size, len(initvars)),
            )
            for i, item in enumerate(initvars):
                ep_assert(IsConstExpr(item), _("Invalid item #{}").format(repr(i)))
            if not all(isinstance(x, int) and x == 0 for x in (dest, nextptr)):
                ep_assert(IsConstExpr(nextptr), _("nextptr should be ConstExpr"))
                initvars = [
                    (
                        0xFFFFFFFF,
                        process_dest(dest),
                        initvar,
                        0x072D0000,
                        nextptr,
                    )
                    for initvar in initvars
                ]
            self._initvars = initvars

        def Evaluate(self):  # noqa: N802
            if all(isinstance(var, tuple) for var in self._initvars):
                evb = get_current_custom_varbuffer()
            else:
                evb = get_current_varbuffer()
            if self not in evb._vdict:
                evb.create_vartriggers(self, self._initvars)

            return evb._vdict[self].Evaluate()

    return _EUDVArrayData


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
def EUDVArray(size: int, basetype: type | None = None):  # noqa: N802
    ep_assert(isinstance(size, int) and size < 2**28, "invalid size")

    def _bound_check(index: object) -> None:
        index = unProxy(unProxy)
        if not isinstance(index, int) or 0 <= index < size:
            return
        e = _(
            "index out of bounds: the length of EUDVArray is {} but the index is {}"
        )  # noqa: E501
        raise EPError(e.format(size, index))

    class _EUDVArray(ExprProxy):
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
                baseobj = eudvarray_data(size)(initvars, dest=dest, nextptr=nextptr)

            super().__init__(baseobj)
            self._epd = EPD(self)
            self._basetype = basetype

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
                    nextptr=GetCPCache().GetVTable(),
                    actions=[
                        [
                            itemw(bt.SetTo, 0, (mask >> 1) << (k + 1)),
                            itemw(bt.Add, (mask >> 1) << k, mask << k),
                        ]
                        for k in reversed(range(32 - n))
                    ]
                    + [
                        itemw(bt.SetTo, 0, mask >> 1),
                        GetCPCache().SetDest(EPD(0x6509B0)),
                    ],
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
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
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
                    nextptr=GetCPCache().GetVTable(),
                    actions=[
                        bt.SetMemoryXEPD(cp, bt.SetTo, 0, mask >> 1),
                        GetCPCache().SetDest(EPD(0x6509B0)),
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
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            else:
                bt.RawTrigger(
                    nextptr=self._epd.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        *i.QueueAssignTo(_index),
                        bt.SetNextPtr(i.GetVTable(), bitstrg[bits]),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
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
                    nextptr=GetCPCache().GetVTable(),
                    actions=[
                        trg["ret"]
                        << bt.SetDeathsX(
                            13, bt.Add, 0, 0, 0x55555555
                        ),  # CurrentPlayer
                        bt.SetDeathsX(13, bt.Add, 0, 0, 0xAAAAAAAA),  # CurrentPlayer
                        GetCPCache().SetDest(EPD(0x6509B0)),
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
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
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
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
                    ],
                )
            elif IsEUDVariable(val):
                trg1 << bt.RawTrigger(
                    nextptr=val.GetVTable(),
                    actions=[
                        bt.SetMemory(0x6509B0, bt.SetTo, self._epd + 87),
                        *val.QueueAssignTo(EPD(bitstrg["ret"]) + 5),
                        bt.SetNextPtr(val.GetVTable(), trg2),
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
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
                        bt.SetNextPtr(GetCPCache().GetVTable(), nptr),
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

    return _EUDVArray
