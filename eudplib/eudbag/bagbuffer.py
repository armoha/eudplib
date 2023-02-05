#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2023 by Armoha.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.
import math
from collections import deque
from ..core.allocator.payload import _PayloadHelper
from .. import core as c
from .. import utils as ut
from .layout import _overlap_distance


class EUDBagBuffer(c.EUDObject):
    def __init__(self, var_count):
        super().__init__()
        self._vdict = {}
        self._var_count = var_count
        self._overlap_distance = _overlap_distance[var_count]
        self._stacking_count = math.floor(328 / self._overlap_distance)
        self._nptrs = list()
        self._acts = list()

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, nptr, init_acts):
        # init_acts = ((bitmask, player, #, modifier), ...)
        ret = self + (self._overlap_distance * self._acts - 4)
        self._nptrs.append(nptr)
        self._acts.append(init_acts)
        if v is not None:
            self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, nptr, init_acts_list):
        ret = self + (self._overlap_distance * self._acts - 4)
        for init_acts in init_acts_list:
            self.CreateVarTrigger(None, nptr, init_acts)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2376 + self._overlap_distance * (self._acts - 1)

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
            for i in range(32 + count):
                emitbuffer.WriteDword(self._nptrs[i]) if i < count else emitbuffer.WriteSpace(4)
                emitbuffer.WriteSpace(15)
                emitbuffer.WriteByte(0) if i < count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(2)
                emitbuffer.WriteByte(0) if 5 <= i < 5 + count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(13)
                if 4 <= i < 4 + count:
                    initvals = self._acts[i - 4]
                    emitbuffer.WriteDword(initvals[0])  # bitmask
                    emitbuffer.WriteSpace(12)
                    emitbuffer.WriteDword(initvals[1])  # player
                    emitbuffer.WriteDword(initvals[2])
                    emitbuffer.WriteDword(initvals[3])  # unit, acttype, SetTo
                    emitbuffer.WriteDword(0x43530000)  # actflag, SC
                else:
                    emitbuffer.WriteSpace(32)
                emitbuffer.WriteByte(4) if 32 <= i else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(3)
