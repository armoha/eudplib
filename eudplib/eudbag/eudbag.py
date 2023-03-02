#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

"""EUDBag type

- `Bag` in Artemis Framework
- Generalization of EUDVArray
- Fast to iterate, add and remove
- Fixed capacity, nextptr and destPlayer
- Unstable collection; removing item changes items' order
- Has length
"""

import functools
from collections.abc import Iterator
from typing import Literal

from .. import core as c
from .. import ctrlstru as cs
from ..ctrlstru.loopblock import _UnsafeWhileNot
from ..eudlib import f_setcurpl2cpcache
from ..localize import _
from ..utils import EPD, EPError, EUDPeekBlock, ep_assert
from .bagbuffer import BagTriggerForward
from .layout import _overlap_distance


def _parse_subobject(fieldlist) -> Iterator[tuple[str, type | None, Literal["var", "const"]]]:
    for field in fieldlist:
        # "fieldname"
        if isinstance(field, str):
            yield field, None, "var"
            continue
        # ("fieldname", type)
        if len(field) == 2:
            yield field[0], field[1], "var"
            continue
        # ("fieldname", type, "const")
        if len(field) == 3:
            yield field[0], field[1], field[2]
            continue


@functools.cache
def _write_var(fieldcount: int) -> tuple[c.RawTrigger, c.RawTrigger, dict[int, c.ConstExpr]]:
    c.PushTriggerScope()
    var = {}
    actions = []  # [c.SetMemory(0x6509B0, c.SetTo, 0)]
    for t in range(3):
        for i in range(t, fieldcount, 3):
            action = c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, i // 3 * 2)
            var[i] = EPD(action) + 5
            actions.append(action)
        if t < 2:
            actions.append(c.SetMemory(0x6509B0, c.Add, 8))
    triggers = []
    for n in range(0, len(actions), 64):
        trg = c.RawTrigger(actions=actions[n : n + 64])
        triggers.append(trg)
    c.PopTriggerScope()
    return triggers[0], triggers[-1], var


@functools.cache
def _update_var(mutfield_bitset: int) -> tuple[c.RawTrigger, c.RawTrigger, dict[int, c.ConstExpr]]:
    c.PushTriggerScope()
    var = {}
    actions = []  # [c.SetMemory(0x6509B0, c.SetTo, 0)]
    for t in range(3):
        bitset = mutfield_bitset >> t
        i = t
        while bitset > 0:
            if bitset & 1:
                action = c.SetDeaths(c.CurrentPlayer, c.SetTo, 0, i // 3 * 2)
                var[i] = EPD(action) + 5
                actions.append(action)
            i += 3
            bitset >>= 3
        if t < 2:
            actions.append(c.SetMemory(0x6509B0, c.Add, 8))
    triggers = []
    for n in range(0, len(actions), 64):
        trg = c.RawTrigger(actions=actions[n : n + 64])
        triggers.append(trg)
    c.PopTriggerScope()
    return triggers[0], triggers[-1], var


class _Subobject:
    def __init__(self, fields) -> None:
        self._fielddict = fields
        for fieldname, typemut in fields.items():
            if typemut[0]:
                setattr(self, fieldname, typemut[0].cast(c.EUDVariable()))
            else:
                setattr(self, fieldname, c.EUDVariable())
        self._initialized = True

    def setfield(self, name, value):
        # mut = self._fielddict[name][1]
        # ep_assert(mut == "var", _("Can't modify const field {}").format(name))
        getattr(self, name) << value

    def __setattr__(self, name, value):
        if "_initialized" in self.__dict__:
            try:
                self.setfield(name, value)
            except AttributeError as e:
                raise EPError(_("Unknown field name {}").format(name))
        else:
            self.__dict__[name] = value

    def _update(self) -> None:
        mutfield_bitset = 0
        varfields = []
        for i, fieldname in enumerate(self._fielddict):
            if self._fielddict[fieldname][1] == "var":
                mutfield_bitset |= 1 << i
                varfields.append((i, getattr(self, fieldname)))
        if mutfield_bitset == 0:  # every fields are const
            return None

        start, end, var = _update_var(mutfield_bitset)
        nextptr = c.Forward()
        operations = [(var[i], c.SetTo, field) for i, field in varfields]
        operations.append((EPD(end) + 1, c.SetTo, nextptr))
        c.NonSeqCompute(operations)
        c.SetNextTrigger(start)
        nextptr << c.NextTrigger()

    # Specializations

    def iaddattr(self, name, value):
        field = getattr(self, name)
        field += value

    # FIXME: add operator for Subtract
    def isubtractattr(self, name, value):
        field = getattr(self, name)
        c.SeqCompute([(field, c.Subtract, value)])

    def isubattr(self, name, value):
        field = getattr(self, name)
        field -= value

    def imulattr(self, name, value):
        field = getattr(self, name)
        field *= value

    def ifloordivattr(self, name, value):
        field = getattr(self, name)
        field //= value

    def imodattr(self, name, value):
        field = getattr(self, name)
        field %= value

    def ilshiftattr(self, name, value):
        field = getattr(self, name)
        field <<= value

    def irshiftattr(self, name, value):
        field = getattr(self, name)
        field >>= value

    def ipowattr(self, name, value):
        field = getattr(self, name)
        field **= value

    def iandattr(self, name, value):
        field = getattr(self, name)
        field &= value

    def iorattr(self, name, value):
        field = getattr(self, name)
        field |= value

    def ixorattr(self, name, value):
        field = getattr(self, name)
        field ^= value

    # FIXME: Add operator for x[i] = ~x[i]
    def iinvertattr(self, name, value):
        field = getattr(self, name)
        field.iinvert()


class EUDBag:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        if not hasattr(self, "_subobject_"):
            raise EPError(_("_subobject_ is not defined"))
        subobject = self._subobject_
        self.fieldcount: int = len(subobject)
        self.objdistance: int = _overlap_distance[self.fieldcount]
        ep_assert(self.fieldcount > 0, _("subobject field is empty"))
        self.loopvar = BagTriggerForward(0, [[(0xFFFFFFFF, 0, 0, 0x072D0000) for _ in subobject]])
        self.vartrigger = BagTriggerForward(
            self.loopvar,
            [
                [
                    (0xFFFFFFFF, EPD(self.loopvar) + 87 + 8 * i, 0, 0x072D0000)
                    for i in range(self.fieldcount)
                ]
                for _ in range(capacity)
            ],
        )
        self.trg = c.EUDVariable(self.vartrigger + self.objdistance * capacity)
        self.pos = c.EUDVariable(EPD(self.vartrigger) + 87 + self.objdistance // 4 * capacity)
        self._subobject_fields = {
            name: (_type, mut) for name, _type, mut in _parse_subobject(subobject)
        }
        """TODO: Add CurrentPlayer field
        for name, _type, mut in _parse_subobject(subobject):
            # CP trick member
            if initval is c.CurrentPlayer:
                ep_assert(
                    self.cpvar is None,
                    f"Multiple CurrentPlayer members are disallowed: {self.cpvar} and {name}",
                )
                self.cpvar = name
                self.loopvar[name]._vartrigger._initval = (
                    0xFFFFFFFF,
                    c.EncodePlayer(c.CurrentPlayer),
                    0,
                    0x072D0000,
                    0,
                )
        """

    def add(self, *args, **kwargs) -> None:
        if len(args) > len(self._subobject_fields):
            raise TypeError(
                _("{}.add() takes up to {} positional arguments but {} were given").format(
                    self.__class__.__name__, len(self._subobject_fields), len(args)
                )
            )
        for kwarg in kwargs:
            if kwarg not in self._subobject_fields:
                raise TypeError(
                    _("subobject of {} has no field {}").format(
                        self.__class__.__name__, repr(kwarg)
                    )
                )
        field = []
        missing_field = []
        for n, name in enumerate(self._subobject_fields):
            if name in kwargs:
                if n < len(args):
                    raise TypeError(
                        _("{}.add() got multiple values for field {}").format(
                            self.__class__.__name__, repr(name)
                        )
                    )
                field.append(kwargs[name])
            elif n >= len(args):
                missing_field.append(name)
            else:
                field.append(args[n])
        if missing_field:
            raise TypeError(
                _("{}.add() missing {} required positional arguments: {}").format(
                    self.__class__.__name__, len(missing_field), missing_field
                )
            )
        """
        if self.keyword_only:
            missing_kwargs = []
            for kwarg in self.keyword_only:
                if kwarg not in kwargs:
                    missing_kwargs.append(kwarg)
            if missing_kwargs:
                raise TypeError(
                    f"{self.__class__.__name__}.add missing {len(missing_kwargs)} required positional arguments: {missing_kwargs}"
                )
        """
        start, end, var = _write_var(self.fieldcount)
        nptr = c.Forward()
        # FIXME: merge two triggers _write_var and f_setcurpl2cpcache
        c.NonSeqCompute(
            [
                (self.trg, c.Add, -self.objdistance),
                (EPD(0x6509B0), None, self.pos),
                (EPD(end) + 1, c.SetTo, nptr),
            ]
            + [(var[i], c.SetTo, field[i]) for i in range(self.fieldcount)]
        )
        c.SetNextTrigger(start)
        nptr << c.NextTrigger()
        f_setcurpl2cpcache(actions=self.pos.AddNumber(-(self.objdistance // 4)))

    def __iter__(self) -> Iterator[_Subobject]:
        loopstart, pos, loopbody = [c.Forward() for _ in range(3)]
        c.VProc(
            [self.trg, self.pos],
            [
                self.trg.SetDest(EPD(loopstart)),
                self.pos.SetDest(EPD(pos)),
                c.SetMemory(self.loopvar + 4, c.SetTo, loopbody),
            ],
        )

        if _UnsafeWhileNot()(
            c.Memory(loopstart, c.AtLeast, self.vartrigger + self.objdistance * self.capacity)
        ):
            block = EUDPeekBlock("whileblock")[1]
            c.PushTriggerScope()  # remove entry
            remove_end = c.Forward()
            remove_start = c.RawTrigger(
                nextptr=self.trg.GetVTable(),
                actions=[
                    self.trg.SetDest(EPD(self.trg.GetVTable()) + 1),
                    c.SetMemory(self.loopvar + 4, c.SetTo, remove_end),
                    loopvar.SetDest(0),  # pos가 이 액션의 값 칸
                ],
            )
            pos << remove_start + 328 + 32 * 2 + 20
            remove_end << c.RawTrigger(
                actions=[
                    self.trg.AddNumber(self.objdistance),
                    self.pos.AddNumber(self.objdistance // 4),
                    loopvar.SetDest(EPD(0x6509B0)),
                    c.SetMemory(self.loopvar + 4, c.SetTo, loopstart),
                    SetNextPtr(loopvar.GetVTable(), loopbody),
                ]
            )
            c.SetNextTrigger(block["contpoint"])
            c.PopTriggerScope()

            loopstart << block["loopstart"] + 4
            loopbody << c.NextTrigger()

            subobject = _Subobject(self._subobject_fields)
            yield subobject

            cs.EUDSetContinuePoint()
            subobject._update()
            cs.DoActions(
                c.SetMemory(loopstart, c.Add, self.objdistance),
                c.SetMemory(pos, c.Add, self.objdistance // 4),
            )
        cs.EUDEndWhile()
