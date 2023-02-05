#!/usr/bin/python
# -*- coding: utf-8 -*-

from .. import core as c
from ..core.allocator.payload import _PayloadHelper


class EUDJumpBuffer(c.EUDObject):
    """Jump table buffer

    20 bytes per nextptr.
    """

    def __init__(self):
        super().__init__()

        self._jdict = {}
        self._nextptrs = []

    def DynamicConstructed(self):
        return True

    def CreateJumpTrigger(self, v, nextptr):
        ret = self + (20 * len(self._nextptrs) - 4)
        self._nextptrs.append(nextptr)
        self._jdict[v] = ret
        return ret

    def CreateMultipleJumpTriggers(self, v, nextptrs):
        ret = self + (20 * len(self._nextptrs) - 4)
        self._nextptrs.extend(nextptrs)
        self._jdict[v] = ret
        return ret

    def GetDataSize(self):
        return 2376 + 20 * (len(self._nextptrs) - 1)

    def CollectDependency(self, emitbuffer):
        for nextptr in self._nextptrs:
            if type(nextptr) is not int:
                emitbuffer.WriteDword(nextptr)

    def WritePayload(self, emitbuffer):
        count = len(self._nextptrs)
        with _PayloadHelper(emitbuffer) as emitbuffer:
            for i in range(118 + count):
                emitbuffer.WriteDword(self._nextptrs[i]) if i < count else emitbuffer.WriteSpace(4)
                emitbuffer.WriteSpace(6)
                emitbuffer.WriteByte(0) if 16 <= i < 16 + count else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(1)
                emitbuffer.WriteByte(8) if 118 <= i else emitbuffer.WriteSpace(1)
                emitbuffer.WriteSpace(3)
                if i == 118 + count - 1:
                    break
                emitbuffer.WriteSpace(3)
                emitbuffer.WriteByte(0) if i < count else emitbuffer.WriteSpace(1)


_jtb = None


def RegisterNewJumpBuffer():
    global _jtb
    _jtb = EUDJumpBuffer()


def GetCurrentJumpBuffer():
    return _jtb


c.RegisterCreatePayloadCallback(RegisterNewJumpBuffer)


# Unused jump table don't need to be allocated.
class JumpTriggerForward(c.ConstExpr):
    def __init__(self, nextptrs):
        super().__init__(self)
        self._nextptrs = nextptrs

    def Evaluate(self):
        jtb = GetCurrentJumpBuffer()
        try:
            return jtb._jdict[self].Evaluate()
        except KeyError:
            jt = jtb.CreateMultipleJumpTriggers(self, self._nextptrs)
            return jt.Evaluate()
