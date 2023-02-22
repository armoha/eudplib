#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2014 by trgk.
# All rights reserved.
# This file is part of EUD python library (eudplib), and is released under "MIT License Agreement".
# Please see the LICENSE file that should have been included as part of this package.

from collections import deque
from typing import TYPE_CHECKING, Literal

from ... import utils as ut
from .. import rawtrigger as bt
from ..allocator import RegisterCreatePayloadCallback
from ..allocator.payload import _PayloadHelper
from ..eudobj import EUDObject

if TYPE_CHECKING:
    from ..allocator import ConstExpr
    from .eudv import VariableTriggerForward


class EUDVarBuffer(EUDObject):
    """Variable buffer

    72 bytes per variable.
    """

    def __init__(self) -> None:
        super().__init__()

        self._vdict: "dict[VariableTriggerForward, int]" = {}
        self._initvals: "list[int | ConstExpr]" = []

    def DynamicConstructed(self) -> Literal[True]:
        return True

    def CreateVarTrigger(self, v, initval):
        ret = self + (72 * len(self._initvals) - 4)
        self._initvals.append(initval)
        self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + (72 * len(self._initvals) - 4)
        self._initvals.extend(initvals)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self) -> int:
        return 2376 + 72 * (len(self._initvals) - 1)

    def CollectDependency(self, emitbuffer) -> None:
        for initval in self._initvals:
            if type(initval) is not int:
                emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer) -> None:
        count = len(self._initvals)
        with _PayloadHelper(emitbuffer) as emitbuffer:
            for i in range(32 + count):
                emitbuffer.WriteDword(0) if i < count else emitbuffer.WriteSpace(4)
                emitbuffer.WriteSpace(15)  # empty condition
                emitbuffer.WriteByte(0) if i < count else emitbuffer.WriteSpace(1)  # condtype
                emitbuffer.WriteSpace(1)  # empty condition (continued)
                emitbuffer.WriteByte(0) if i < count else emitbuffer.WriteSpace(1)  # condflag
                emitbuffer.WriteByte(0) if 5 <= i < 5 + count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(1)  # empty action2
                emitbuffer.WriteByte(0) if 5 <= i < 5 + count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(11)  # empty action2 (continued)
                if 4 <= i < 4 + count:
                    emitbuffer.WriteDword(0xFFFFFFFF)  # bitmask
                    emitbuffer.WriteSpace(12)  # text string, wav string, time
                    emitbuffer.WriteDword(0)  # player
                    emitbuffer.WriteDword(self._initvals[i - 4])
                    emitbuffer.WriteDword(0x072D0000)  # unit, acttype, SetTo
                    emitbuffer.WriteDword(0x43530000)  # actflag, SC
                else:
                    emitbuffer.WriteSpace(32)  # empty action1
                emitbuffer.WriteByte(4) if 32 <= i else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(3)  # trigger flags


_evb = None


def RegisterNewVariableBuffer() -> None:
    global _evb
    _evb = EUDVarBuffer()


def GetCurrentVariableBuffer():
    return _evb


RegisterCreatePayloadCallback(RegisterNewVariableBuffer)


class EUDCustomVarBuffer(EUDObject):
    """Customizable Variable buffer

    72 bytes per variable.
    """

    def __init__(self):
        super().__init__()

        self._vdict = {}
        self._nptrs = []
        self._acts = []

    def DynamicConstructed(self):
        return True

    def CreateVarTrigger(self, v, initval):
        # bitmask, player, #, modifier, nptr
        ret = self + (72 * len(self._acts) - 4)
        self._nptrs.append(initval[4])
        self._acts.append(initval[0:4])
        if v is not None:
            self._vdict[v] = ret
        return ret

    def CreateMultipleVarTriggers(self, v, initvals):
        ret = self + (72 * len(self._acts) - 4)
        for initval in initvals:
            self.CreateVarTrigger(None, initval)
        self._vdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2376 + 72 * (len(self._acts) - 1)

    def CollectDependency(self, emitbuffer):
        for nptr in self._nptrs:
            if type(nptr) is not int:
                emitbuffer.WriteDword(nptr)
        for initvals in self._acts:
            for initval in initvals:
                if type(initval) is not int:
                    emitbuffer.WriteDword(initval)

    def WritePayload(self, emitbuffer):
        count = len(self._acts)
        with _PayloadHelper(emitbuffer) as emitbuffer:
            for i in range(32 + count):
                emitbuffer.WriteDword(self._nptrs[i]) if i < count else emitbuffer.WriteSpace(4)
                emitbuffer.WriteSpace(15)  # empty condition
                emitbuffer.WriteByte(0) if i < count else emitbuffer.WriteSpace(1)  # condtype
                emitbuffer.WriteSpace(1)  # empty condition (continued)
                emitbuffer.WriteByte(0) if i < count else emitbuffer.WriteSpace(1)  # condflag
                emitbuffer.WriteByte(0) if 5 <= i < 5 + count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(1)  # empty action2
                emitbuffer.WriteByte(0) if 5 <= i < 5 + count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(11)  # empty action2 (continued)
                if 4 <= i < 4 + count:
                    initvals = self._acts[i - 4]
                    emitbuffer.WriteDword(initvals[0])  # bitmask
                    emitbuffer.WriteSpace(12)  # text string, wav string, time
                    emitbuffer.WriteDword(initvals[1])  # player
                    emitbuffer.WriteDword(initvals[2])
                    emitbuffer.WriteDword(initvals[3])  # unit, acttype, SetTo
                    emitbuffer.WriteDword(0x43530000)  # actflag, SC
                else:
                    emitbuffer.WriteSpace(32)  # empty action1
                emitbuffer.WriteByte(4) if 32 <= i else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(3)  # trigger flags


_ecvb = None


def RegisterNewCustomVariableBuffer():
    global _ecvb
    _ecvb = EUDCustomVarBuffer()


def GetCurrentCustomVariableBuffer():
    return _ecvb


RegisterCreatePayloadCallback(RegisterNewCustomVariableBuffer)
