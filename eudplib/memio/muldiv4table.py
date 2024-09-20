# Copyright 2024 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib),
# and is released under "MIT License Agreement". Please see the LICENSE
# file that should have been included as part of this package.

from collections.abc import Callable

from .. import core as c
from .. import utils as ut
from .rwcommon import lv

# muldiv4_table[frozenset(strides)][msb_index]
muldiv4_table: dict[frozenset[int], dict[int, c.RawTrigger]] = {}
muldiv_end_table: dict[int, c.RawTrigger] = {}
varcount_dict: dict[frozenset[int], int] = {}


def _varcount(strides: frozenset[int]) -> int:
    count = 0
    for x in strides:
        if x % 4 == 0:
            count += 1
        else:
            count += 2
    return count


def _get(msb_index: int, strides: frozenset[int]) -> c.RawTrigger:
    stride_table = muldiv4_table[strides]
    return stride_table[msb_index]


def _insert(msb_index: int, strides: frozenset[int]) -> c.RawTrigger:
    try:
        stride_table = muldiv4_table[strides]
    except KeyError:
        stride_table = {}
        muldiv4_table[strides] = stride_table
    try:
        trigger = stride_table[msb_index]
    except KeyError:
        try:
            varcount = varcount_dict[strides]
        except KeyError:
            varcount = _varcount(strides)
            varcount_dict[strides] = varcount

        c.PushTriggerScope()
        try:
            read_end = muldiv_end_table[varcount]
        except KeyError:
            _end = c.Forward()
            actions = [c.SetDeaths(0, c.SetTo, 0, 0) for _ in range(varcount)]
            actions.extend(
                c.SetMemory(_end + 348 + 32 * i, c.SetTo, 0) for i in range(varcount)
            )
            read_end = c.RawTrigger(nextptr=0, actions=actions)
            _end << read_end
            muldiv_end_table[varcount] = read_end

        for x in range(0, msb_index + 1):
            if x in stride_table:
                continue
            actions = []
            index = 0
            read_act = read_end + 348

            def append(t):
                nonlocal index
                if t != 0:
                    actions.append(c.SetMemory(read_act + 32 * index, c.Add, t))
                index += 1

            for k in sorted(strides):
                q, r = divmod(k << x, 4)
                append(q)
                if k % 4 != 0:
                    append(r)

            if x != 0:
                trig = c.RawTrigger(
                    nextptr=stride_table[x - 1],
                    conditions=lv.AtLeastX(1, 1 << x),
                    actions=actions,
                )
            else:
                trig = c.RawTrigger(
                    conditions=lv.AtLeastX(1, 1 << x), actions=actions
                )
                # carry 4 subp -> 1 epd
                index = 0
                for k in sorted(strides):
                    if k % 4 == 0:
                        index += 1
                        continue
                    if k % 4 != 3:
                        dst = read_act + 32 * index
                        c.RawTrigger(
                            conditions=c.Memory(dst + 32, c.AtLeast, 4),
                            actions=[
                                c.SetMemory(dst + 32, c.Subtract, 4),
                                c.SetMemory(dst, c.Add, 1),
                            ],
                        )
                    index += 2
                c.SetNextTrigger(read_end)
            stride_table[x] = trig
        c.PopTriggerScope()
        trigger = stride_table[msb_index]

    return trigger


def _insert_or_get(msb_index: int, strides: frozenset[int]) -> c.RawTrigger:
    try:
        return _get(msb_index, strides)
    except KeyError:
        return _insert(msb_index, strides)


def _caller(msb_index: int, strides: frozenset[int]) -> Callable:
    readtrg = _insert_or_get(msb_index, strides)
    varcount = varcount_dict[strides]
    read_end = muldiv_end_table[varcount]

    def f(
        var: c.EUDVariable, *derived_vars: c.EUDVariable
    ) -> tuple[c.RawTrigger, c.RawTrigger]:
        ut.ep_assert(len(derived_vars) == varcount)
        c.PushTriggerScope()
        _jump_trg = c.Forward()
        jump_trg = c.RawTrigger(
            conditions=var.Exactly(0),
            actions=c.SetNextPtr(_jump_trg, 0),
        )
        _jump_trg << jump_trg
        jump_restore = c.VProc(var, var.QueueAssignTo(ut.EPD(jump_trg) + 4))
        actions = [
            # c.SetNextPtr(read_end, 0),  # this is set by ArrayMember.get_epd
            c.SetNextPtr(var.GetVTable(), readtrg),
            var.SetDest(lv),
        ]
        actions.extend(
            c.SetMemory(read_end + 344 + 32 * i, c.SetTo, ut.EPD(v.getValueAddr()))
            for i, v in enumerate(derived_vars)
        )
        c.RawTrigger(nextptr=var.GetVTable(), actions=actions)
        c.PopTriggerScope()
        return jump_trg, jump_restore

    return f
