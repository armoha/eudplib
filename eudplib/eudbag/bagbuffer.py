#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.
import functools

from .. import core as c
from .. import utils as ut
from ..core.allocator.payload import _PayloadHelper
from . import layout


class BagTriggerForward(c.ConstExpr):
    def __init__(self, nptr, init_acts_list) -> None:
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
        self._acts: list[list[int | c.ConstExpr]] = list()

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, nptr, init_acts):
        # init_acts = ((bitmask, player, #, modifier), ...)
        ret = self + (self._overlap_distance * len(self._acts) - 4)
        self._nptrs.append(nptr)
        self._acts.append(init_acts)
        if v is not None:
            self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, nptr, init_acts_list):
        ret = self + (self._overlap_distance * len(self._acts) - 4)
        for init_acts in init_acts_list:
            self.CreateVarTrigger(None, nptr, init_acts)
        self._vdict[v] = ret
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


@functools.cache
def GetCurrentBagBuffer(var_count: int) -> EUDBagBuffer:
    return EUDBagBuffer(var_count)
