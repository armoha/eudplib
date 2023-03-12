#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.
import functools
from collections.abc import Sequence

from .. import core as c
from .. import utils as ut
from ..core.allocator import RegisterCreatePayloadCallback
from ..core.allocator.payload import _PayloadHelper
from ..localize import _
from . import layout


class BagTriggerForward(c.ConstExpr):
    def __init__(
        self, nptr, init_acts_list: Sequence[Sequence[Sequence[int | c.ConstExpr]]]
    ) -> None:
        super().__init__(self)
        self._nptr = nptr
        self._init_acts_list = init_acts_list

    def Evaluate(self):
        bb = GetCurrentBagBuffer(len(self._init_acts_list[0]))
        try:
            return bb._vdict[self].Evaluate()
        except KeyError:
            vt = bb.CreateMultipleVarTriggers(self, self._nptr, self._init_acts_list)
            return vt.Evaluate()


class EUDBagBuffer(c.EUDObject):
    def __init__(self, var_count: int) -> None:
        ut.ep_assert(1 <= var_count <= 64)
        super().__init__()
        self._vdict: dict[BagTriggerForward, c.ConstExpr] = {}
        self._var_count = var_count
        self._overlap_distance = layout._overlap_distance[var_count]
        self._nptrs: list[int | c.ConstExpr] = list()
        self._acts: list[Sequence[Sequence[int | c.ConstExpr]]] = list()

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, nptr, init_acts: Sequence[Sequence[int | c.ConstExpr]]):
        # init_acts = ((bitmask, player, #, modifier), ...)
        ret = self + (self._overlap_distance * len(self._acts) - 4)
        self._nptrs.append(nptr)
        ut.ep_assert(len(init_acts) == self._var_count)
        ut.ep_assert(all(len(action) == 4 for action in init_acts))
        self._acts.append(init_acts)
        if v is not None:
            self._vdict[v] = ret  # type: ignore[assignment]
        return ret

    def CreateMultipleVarTriggers(
        self, v, nptr, init_acts_list: Sequence[Sequence[Sequence[int | c.ConstExpr]]]
    ):
        ret = self + (self._overlap_distance * len(self._acts) - 4)
        for init_acts in init_acts_list:
            self.CreateVarTrigger(None, nptr, init_acts)
        self._vdict[v] = ret  # type: ignore[assignment]
        return ret

    def GetDataSize(self):
        return 2376 + self._overlap_distance * (len(self._acts) - 1)

    def CollectDependency(self, emitbuffer):
        for nptr in self._nptrs:
            if type(nptr) is not int:
                emitbuffer.WriteDword(nptr)
        for init_acts in self._acts:
            for action in init_acts:
                for action_arg in action:
                    if type(action_arg) is not int:
                        emitbuffer.WriteDword(action_arg)

    def WritePayload(self, emitbuffer):
        count = len(self._acts)
        with _PayloadHelper(emitbuffer) as emitbuffer:
            layout._write_payload[self._var_count](emitbuffer, count, self._nptrs, self._acts)


_bb: list[EUDBagBuffer | None] = [None] * 64


def RegisterNewBagBuffer() -> None:
    global _bb
    for n in range(64):
        _bb[n] = EUDBagBuffer(n + 1)


def GetCurrentBagBuffer(var_count: int) -> EUDBagBuffer:
    buffer = _bb[var_count - 1]
    if buffer is None:
        raise ut.EPError(_("Failed to initialize EUDBagBuffer(var_count={})").format(var_count))
    return buffer


RegisterCreatePayloadCallback(RegisterNewBagBuffer)
